"""Chinese/English presentation and unchanged source/edit values, isolated DB.
All publications/metrics below are synthetic test-only records, not real results.
"""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import os,socket,subprocess,tempfile,time
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def run():
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    with tempfile.TemporaryDirectory() as directory:
        env={**os.environ,'DATABASE_PATH':directory+'/test.db','X_LIVE_ENABLED':'false','X_BEARER_TOKEN':'','OPENAI_API_KEY':''}
        server=subprocess.Popen(['python','-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    with socket.create_connection(('127.0.0.1',port),timeout=.1):break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Test server did not start')
            with sync_playwright() as p:
                browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
                context=browser.new_context(viewport={'width':1440,'height':1100})
                external=[];errors=[]
                def local_only(route):
                    if route.request.url.startswith(base+'/'):route.continue_()
                    else:external.append(route.request.url);route.abort()
                context.route('**/*',local_only)
                page=context.new_page();page.set_default_timeout(8000);page.set_default_navigation_timeout(8000);page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(base);page.locator('.topic').first.wait_for()
                page.wait_for_function("document.documentElement.lang==='zh-CN'")
                assert page.locator('[data-tab="sources"]').inner_text().strip().endswith('数据源与监控设置')
                assert '历史数据不足' in page.locator('#topic-list').inner_text()
                assert '为何与 TelyClaw 相关' in page.locator('#detail').inner_text()
                assert '多个独立账号支持' in page.locator('.topic').first.inner_text()
                page.locator('#detail details').last.locator('summary').click()
                # Protect raw post text even if it happens to equal an interface key.
                now=datetime.now(timezone.utc)
                # Test-only engineering concerns; no real source text or results.
                discussions=[
                    'A coding agent needs error feedback to recover from failed changes.',
                    'A programming agent should troubleshoot failures with tests and verification.',
                    'A coding assistant filters tool output from context and retains session memory after compaction.',
                    'A coding agent harness can execute complex software engineering tasks.',
                ]
                for i,text in enumerate(discussions):
                    payload={'url':f'https://x.com/quality_{i}/status/{990001+i}',
                             'handle':f'quality_{i}','text':text,
                             'created_at':(now-timedelta(minutes=20)).isoformat()}
                    assert page.request.post(base+'/api/manual/posts',data=payload).status==201
                page.locator('[data-tab="opportunities"]').click()
                page.locator('#mode').select_option('manual');page.locator('#window').select_option('168');page.locator('#analyze').click()
                page.locator('.topic').first.wait_for()
                page.wait_for_function("document.getElementById('detail').textContent.includes('共同讨论洞察')")
                assert 'AI 编程智能体的工程化与可靠性' in page.locator('#detail h2').inner_text()
                narrative=page.locator('#detail [data-i18n-en]').first
                assert '所选 4 条帖子中，4 条' in narrative.inner_text()
                assert '不代表行业共识或讨论量正在加速' in narrative.inner_text()
                assert all('@quality_'+str(i) in narrative.inner_text() for i in range(4))
                assert '上下文与 Token 效率' in narrative.inner_text()
                assert 'compaction, tool output' in page.locator('#detail details').first.text_content()
                assert '历史数据不足' in page.locator('.topic').first.inner_text()
                page.locator('[data-language="en"]').click()
                assert '4 of 4 selected posts' in narrative.inner_text()
                assert 'not evidence of consensus or accelerating discussion' in narrative.inner_text()
                page.locator('[data-language="zh"]').click()
                assert '所选 4 条帖子中，4 条' in narrative.inner_text()
                page.locator('#mode').select_option('demo');page.locator('#analyze').click()
                page.locator('.topic').first.wait_for()
                raw='Performance'
                payload={'url':'https://x.com/test_fixture/status/900001','handle':'test_fixture','text':raw,'created_at':(now-timedelta(minutes=20)).isoformat()}
                assert page.request.post(base+'/api/manual/posts',data=payload).status==201
                page.locator('[data-tab="sources"]').click()
                page.reload();page.locator('#manual-list .evidence').first.wait_for(state='attached')
                page.locator('[data-tab="sources"]').click()
                assert page.locator('#manual-list [data-raw]').filter(has_text=raw).inner_text()==raw
                page.locator('#manual-text').fill('English source text must stay unchanged. 中文原文亦保留。')
                page.locator('#manual-handle').fill('@another_author')
                original_brief=page.locator('#positioning').input_value()
                page.locator('[data-language="en"]').click()
                assert page.locator('#manual-text').input_value()=='English source text must stay unchanged. 中文原文亦保留。'
                assert page.locator('#positioning').input_value()==original_brief
                page.locator('[data-language="zh"]').click()
                page.locator('#manual-url').fill(payload['url']);page.locator('#manual-handle').fill('test_fixture')
                page.locator('#manual-time').fill((now-timedelta(minutes=20)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M'))
                page.locator('#save-manual').click()
                page.wait_for_function("document.getElementById('manual-result').textContent.includes('已手动导入')")
                page.locator('[data-tab="opportunities"]').click();page.locator('#generate').click();page.locator('#draft-text').wait_for()
                english_draft=page.locator('#draft-text').input_value()
                angle=page.locator('.angle p').first.inner_text()
                modified='Original English editorial judgment. Human approval stays required.'
                page.locator('#draft-text').fill(modified)
                page.locator('[data-language="en"]').click()
                assert page.locator('#draft-text').input_value()==modified
                assert page.locator('.angle p').first.inner_text()==angle
                assert 'Unsaved' in page.locator('#save-state').inner_text()
                page.locator('[data-language="zh"]').click()
                assert page.locator('#draft-text').input_value()==modified
                assert '尚未保存' in page.locator('#save-state').inner_text()
                page.locator('#approve-draft').click();page.locator('#published-url').wait_for()
                assert page.locator('#export-draft').is_visible()
                draft=page.request.get(base+'/api/state').json()['drafts'][0]
                export=page.request.get(base+f'/api/drafts/{draft["id"]}/export')
                assert export.text()==modified
                composer=page.request.get(base+f'/api/drafts/{draft["id"]}/composer',max_redirects=0)
                assert composer.status==303 and 'intent/tweet?' in composer.headers['location']
                page.locator('#published-url').fill('https://x.com/test_brand/status/900002')
                pubtime=(now-timedelta(minutes=1)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M')
                page.locator('#published-time').fill(pubtime)
                page.locator('[data-language="en"]').click()
                assert page.locator('#published-url').input_value().endswith('/900002')
                assert page.locator('#published-time').input_value()==pubtime
                page.locator('[data-language="zh"]').click();page.locator('#mark-published').click();page.locator('#revision').wait_for()
                page.locator('[data-tab="performance"]').click();page.locator('#metrics-form').wait_for()
                page.wait_for_function("document.getElementById('save-metrics').textContent==='保存衡量记录'")
                assert '未衡量' in page.locator('#performance-totals').inner_text()
                assert page.locator('#measurement-editor [data-raw]').text_content()==modified
                page.locator('#metric-likes').fill('7')
                page.locator('[data-language="en"]').click()
                assert page.locator('#metric-likes').input_value()=='7'
                page.locator('[data-language="zh"]').click();page.locator('#save-metrics').click()
                page.wait_for_function("document.getElementById('performance-totals').textContent.includes('7')")
                assert '已衡量互动量' in page.locator('#performance-formula').inner_text()
                # UI switches are read-only: no record rewriting or new network fetches.
                before=page.request.get(base+'/api/state').json()
                page.locator('[data-language="en"]').click()
                page.reload();page.locator('.topic').first.wait_for()
                assert page.locator('html').get_attribute('lang')=='en'
                after=page.request.get(base+'/api/state').json()
                assert before==after
                assert 'Opportunities' in page.locator('[data-tab="opportunities"]').inner_text()
                page.locator('[data-language="zh"]').click();page.reload();page.locator('.topic').first.wait_for()
                assert page.locator('html').get_attribute('lang')=='zh-CN'
                for tab in ['opportunities','review','performance','sources']:
                    page.locator(f'[data-tab="{tab}"]').click()
                    if tab=='performance':page.locator('#metrics-form').wait_for()
                    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),tab
                    page.screenshot(path=f'work/bilingual-{tab}-zh.png',full_page=True)
                page.locator('[data-tab="opportunities"]').click();page.locator('#mode').select_option('live')
                page.wait_for_function("document.getElementById('live-status').textContent.includes('X_BEARER_TOKEN')")
                assert '未发送 X 请求' in page.locator('#live-status').inner_text()
                page.locator('[data-language="en"]').click()
                assert 'No X request was made' in page.locator('#live-status').inner_text()
                for text in ['X denied access (403). Verify your app permissions, API plan and endpoint access.',
                             'X reported a payment or credit restriction. Check your X Developer billing and access; this app does not purchase credits.',
                             'X rate limit reached (429). Wait until the retry time shown; automatic retry is off.',
                             'Value error, Full post text cannot be blank',
                             'likes: Input should be greater than or equal to 0']:
                    result=page.evaluate('(value)=>{uiLanguage="zh";return tr(value)}',text)
                    assert result!=text,(text,result)
                assert not errors,errors
                assert not external,external
                browser.close()
        finally:server.terminate();server.wait(timeout=10)
    print('Bilingual browser smoke passed: Chinese default, persistence, raw evidence, edits, approval/export/composer, publication and real-metric forms; no external calls.')

if __name__=='__main__':run()
