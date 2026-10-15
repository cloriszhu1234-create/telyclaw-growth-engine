"""Single-post subjects and separate evidence labels. Synthetic fixtures only."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import socket
import subprocess
import sys
import tempfile
import time
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def run():
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    with tempfile.TemporaryDirectory() as directory:
        env = {**os.environ, 'DATABASE_PATH':directory+'/subjects.db',
               'X_LIVE_ENABLED':'false', 'X_BEARER_TOKEN':'', 'OPENAI_API_KEY':''}
        server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app',
            '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    with socket.create_connection(('127.0.0.1', port), timeout=.1):
                        break
                except OSError:
                    time.sleep(.1)
            else:
                raise RuntimeError('Singleton test server did not start')
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
                context = browser.new_context(viewport={'width':1440, 'height':1100})
                external, errors = [], []
                def local_only(route):
                    if route.request.url.startswith(base+'/'):
                        route.continue_()
                    else:
                        external.append(route.request.url)
                        route.abort()
                context.route('**/*', local_only)
                page = context.new_page()
                page.set_default_timeout(8000)
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(base)
                page.locator('.topic').first.wait_for()
                texts = [
                    'Every AI agent can choose a different framework for its task.',
                    'An engineer shares a template with a prompt for the engineering lead.',
                    'Satellite sensors measure coastal erosion after heavy rain.',
                ]
                now = datetime.now(timezone.utc)
                for i, text in enumerate(texts):
                    r = page.request.post(base+'/api/manual/posts', data={
                        'url':f'https://x.com/subject_{i}/status/{970000+i}', 'handle':f'subject_{i}',
                        'text':text, 'created_at':(now-timedelta(minutes=20)).isoformat()})
                    assert r.status == 201, r.text()
                saved = page.request.get(base+'/api/manual/posts').json()
                page.locator('#mode').select_option('manual')
                page.locator('#window').select_option('168')
                page.locator('#analyze').click()
                page.wait_for_function("document.getElementById('topic-list').textContent.includes('AI Agent 的框架选择')")
                titles = page.locator('.topic h3').all_inner_texts()
                assert len(titles) == 3
                assert '工程管理场景的提示词模板' in titles
                assert any(t.startswith('原帖议题：「') for t in titles)
                assert all('待确认的单帖信号' not in t for t in titles)
                for card in page.locator('.topic').all():
                    assert '单一来源信号' in card.inner_text() and '历史数据不足' in card.inner_text()
                output = ROOT/'work/browser'
                output.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(output/'singleton-subjects-zh.png'), full_page=True)
                page.locator('.topic').filter(has_text='AI Agent 的框架选择').click()
                assert page.locator('#detail h2').inner_text() == 'AI Agent 的框架选择'
                assert '不代表独立来源支持' in page.locator('#detail').inner_text()
                # The full source stays verbatim in either UI language.
                page.locator('#detail details').last.locator('summary').click()
                assert page.locator('#detail .evidence p[data-raw]').inner_text() == texts[0]
                page.locator('[data-language="en"]').click()
                assert page.locator('#detail h2').inner_text() == 'AI Agent Framework Selection'
                assert 'Single-source signal' in page.locator('.topic').first.inner_text()
                assert any(t.startswith('Source topic: “') for t in page.locator('.topic h3').all_inner_texts())
                assert page.locator('#detail .evidence p[data-raw]').inner_text() == texts[0]
                page.locator('[data-language="zh"]').click()
                page.locator('#generate').click()
                page.locator('#draft-text').wait_for()
                assert page.locator('#editor h2').inner_text() == 'AI Agent 的框架选择'
                assert page.locator('.angle').count() == 3
                edited = 'A test-only editorial question still needs human review before approval.'
                page.locator('#draft-text').fill(edited)
                page.locator('#approve-draft').click()
                page.locator('#published-url').wait_for()
                with page.expect_download() as download:
                    page.locator('#export-draft').click()
                assert Path(download.value.path()).read_text() == edited
                page.reload()
                page.locator('.topic').first.wait_for()
                page.locator('[data-tab="review"]').click()
                page.locator('[data-draft]').first.click()
                page.locator('#draft-text').wait_for()
                assert page.locator('#draft-text').input_value() == edited
                assert page.locator('#editor h2').inner_text() == 'AI Agent 的框架选择'
                assert page.request.get(base+'/api/manual/posts').json() == saved
                assert page.request.get(base+'/api/x/status').json()['requests_used'] == 0
                assert page.request.get(base+'/api/performance').json()['posts'] == []
                page.set_viewport_size({'width':390, 'height':844})
                assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
                assert not errors, errors
                assert not external, external
                browser.close()
        finally:
            server.terminate()
            server.wait(timeout=10)
    print('PASS: bilingual single-post subjects, quoted fallback, separate source/history labels, unchanged raw sources, edit/approval/TXT/reload and mobile; no external calls.')


if __name__ == '__main__':
    run()
