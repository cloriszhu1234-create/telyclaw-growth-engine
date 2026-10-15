"""Page-source banner regression. Isolated test-only records, no external calls."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import os,socket,subprocess,sys,tempfile,time
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def run():
    with socket.socket() as listener:
        listener.bind(('127.0.0.1',0));port=listener.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    with tempfile.TemporaryDirectory() as directory:
        env={**os.environ,'DATABASE_PATH':directory+'/banner.db','X_LIVE_ENABLED':'false','X_BEARER_TOKEN':'','OPENAI_API_KEY':''}
        server=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    with socket.create_connection(('127.0.0.1',port),timeout=.1):break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Banner test server did not start')
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
                context=browser.new_context(viewport={'width':1440,'height':1100})
                external=[];errors=[]
                def local_only(route):
                    if route.request.url.startswith(base+'/'):route.continue_()
                    else:external.append(route.request.url);route.abort()
                context.route('**/*',local_only)
                page=context.new_page();page.set_default_timeout(8000)
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(base);page.locator('.topic').first.wait_for()
                def banner(label):
                    page.wait_for_function('(value)=>document.getElementById("mode-label").textContent===value',arg=label)
                banner('演示工作台')
                page.locator('[data-tab="review"]').click();banner('内容工作室')
                assert '请选择草稿' in page.locator('#provenance').inner_text()
                page.locator('[data-tab="performance"]').click();banner('发布与表现记录')
                assert '未经 X API 验证' in page.locator('#provenance').inner_text()
                assert '虚构账号' not in page.locator('#provenance').inner_text()
                page.locator('[data-tab="sources"]').click();banner('数据源设置')
                page.locator('[data-language="en"]').click();banner('SOURCE SETTINGS')
                def request(path,payload):
                    r=page.request.post(base+'/api/'+path,data=payload)
                    assert r.ok,r.text()
                    return r.json()
                def create(mode):
                    a=request('analyze',{'mode':mode,'hours':168})
                    return request('drafts',{'analysis_id':a['id'],'topic_id':a['topics'][0]['id']})
                # Two source modes among saved publications: all URLs and values
                # below are explicitly test-only fixtures, never actual results.
                demo=create('demo')
                now=datetime.now(timezone.utc)
                for i,text in enumerate(['A coding agent needs error feedback.', 'A programming assistant requires test verification.']):
                    request('manual/posts',{'url':f'https://x.com/banner_test_{i}/status/{880000+i}',
                        'handle':f'banner_test_{i}','text':text,'created_at':(now-timedelta(minutes=20)).isoformat()})
                manual=create('manual')
                for i,d in enumerate([demo,manual]):
                    request('drafts/'+d['id']+'/approve',{})
                    pub=request('drafts/'+d['id']+'/publish',{'url':f'https://x.com/banner_brand/status/{881000+i}',
                        'published_at':(now-timedelta(minutes=1)).isoformat()})
                    if d['id']==manual['id']:
                        for count in (2,3):request('publications/'+pub['id']+'/measurements',{
                            'impressions':count,'measured_at':datetime.now(timezone.utc).isoformat()})
                revision=request('drafts/'+manual['id']+'/revision',{})
                before=page.request.get(base+'/api/performance').json()
                page.reload();page.locator('.topic').first.wait_for();banner('DEMO WORKSPACE')
                # Every radar mode keeps its own notice; Performance never
                # inherits it, including when mode switches finish asynchronously.
                for mode,label in [('demo','DEMO WORKSPACE'),('manual','MANUAL IMPORTS'),('imported','JSON IMPORTS'),('live','LIVE X · CACHED DATA')]:
                    page.locator('[data-tab="opportunities"]').click()
                    page.locator('#mode').select_option(mode);banner(label)
                    page.locator('[data-tab="performance"]').click();banner('PUBLICATION & PERFORMANCE RECORDS')
                    page.wait_for_function('document.querySelectorAll("[data-publication]").length===2')
                    assert 'not verified through the X API' in page.locator('#provenance').inner_text()
                    assert 'Fictional accounts' not in page.locator('#provenance').inner_text()
                cards=page.locator('#publication-list').inner_text()
                assert 'Source mode: demo' in cards and 'Source mode: manual' in cards
                assert before['aggregate']['totals']['impressions']==3
                assert len(next(x for x in before['posts'] if x['mode']=='manual')['snapshots'])==2
                # A saved draft's mode wins over the radar's Demo selection.
                page.locator('[data-tab="opportunities"]').click();page.locator('#mode').select_option('demo')
                page.locator('[data-tab="review"]').click()
                page.locator(f'[data-draft="{manual["id"]}"]').click();banner('DRAFT SOURCE · Manual Imports')
                assert 'Manually entered X posts' in page.locator('#provenance').inner_text()
                page.locator(f'[data-draft="{demo["id"]}"]').click();banner('DRAFT SOURCE · Demo Data (synthetic)')
                assert 'Fictional accounts' in page.locator('#provenance').inner_text()
                page.locator('[data-language="zh"]').click();banner('草稿来源 · 演示数据（合成）')
                page.locator(f'[data-draft="{revision["id"]}"]').click();banner('草稿来源 · 手动导入')
                edited='Test-only unsaved editorial change.'
                page.locator('#draft-text').fill(edited)
                page.locator('[data-tab="performance"]').click();banner('发布与表现记录')
                page.locator('[data-tab="sources"]').click();banner('数据源设置')
                page.locator('[data-tab="review"]').click();banner('草稿来源 · 手动导入')
                assert page.locator('#draft-text').input_value()==edited
                assert '尚未保存' in page.locator('#save-state').inner_text()
                page.locator('[data-tab="performance"]').click();banner('发布与表现记录')
                page.wait_for_function('document.querySelectorAll("[data-publication]").length===2')
                assert page.request.get(base+'/api/performance').json()==before
                assert page.request.get(base+'/api/x/status').json()['requests_used']==0
                page.screenshot(path=str(ROOT/'work/provenance-performance-zh.png'),full_page=True)
                assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                assert not external,external
                assert not errors,errors
                browser.close()
        finally:server.terminate();server.wait(timeout=10)
    print('PASS: page-specific bilingual banners, all radar modes, mixed publication sources, selected draft, preserved unsaved edits and unchanged metrics; no external calls.')


if __name__=='__main__':run()
