"""Exercise the real app and API. Feedback explicitly marked as test input."""
import json,re,time
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results/browser'
OUT.mkdir(parents=True,exist_ok=True)
SHOTS=ROOT/'docs/screenshots'
SHOTS.mkdir(parents=True,exist_ok=True)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
    page.goto('http://127.0.0.1:8502')
    page.wait_for_load_state('networkidle')
    expect(page.get_by_role('button',name='Run analysis',exact=True)).to_be_visible()
    page.screenshot(path=str(SHOTS/'01-case.png'))
    before={str(f) for f in (ROOT/'runs').glob('*.json')}
    page.get_by_role('button',name='Run analysis',exact=True).click()
    expect(page.get_by_role('heading',name='04 Human review',exact=True)).to_be_visible(timeout=240000)
    new=set(str(f) for f in (ROOT/'runs').glob('*.json'))-before
    # Another CLI case may finish in parallel. Select only the UI case.
    paths=[Path(f) for f in new if Path(f).name.startswith('bank-001-')]
    assert len(paths)==1,paths
    result=json.loads(paths[0].read_text(encoding='utf-8'))
    assert result['status'] in ('complete','partial'),result.get('error')
    assert result['candidates']
    page.get_by_role('heading',name='02 Analysis result',exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(SHOTS/'02-result.png'))
    page.get_by_role('heading',name='03 Evidence workspace',exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(SHOTS/'03-evidence.png'))
    review='Automated UI test: source record inspection works; this is not Dahe Chen\'s acceptance.'
    page.get_by_role('textbox',name='Reason for your judgment',exact=True).fill(review)
    page.get_by_role('button',name='Record judgment',exact=True).click()
    expect(page.get_by_text('Judgment recorded for this run. This is human feedback, not ground truth.',exact=True)).to_be_visible()
    page.get_by_role('heading',name='04 Human review',exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(SHOTS/'04-review-test.png'))
    count_before=len(list((ROOT/'runs').glob('bank-001-*.json')))
    page.get_by_role('combobox',name='Language / 语言',exact=True).click()
    page.get_by_role('option',name='中文',exact=True).click()
    expect(page.get_by_role('heading',name='04 人类核查',exact=True)).to_be_visible()
    expect(page.get_by_role('textbox',name='判断理由',exact=True)).to_have_value(review)
    assert len(list((ROOT/'runs').glob('bank-001-*.json')))==count_before
    with page.expect_download() as download_info:
        page.get_by_role('button',name='导出本次调查',exact=True).click()
    download=download_info.value
    download.save_as(str(OUT/'export.json'))
    exported=json.loads((OUT/'export.json').read_text(encoding='utf-8'))
    assert exported['run_id']==result['run_id']
    assert exported['calls']==result['calls']
    assert exported['human_review']['reason']==review
    page.get_by_role('heading',name='02 分析结果',exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(SHOTS/'05-chinese.png'))
    page.get_by_role('combobox',name='故障案例',exact=True).click()
    page.get_by_role('option',name='bank-004',exact=True).click()
    expect(page.get_by_text('当前案例还没有分析结果。',exact=True)).to_be_visible()
    assert page.get_by_role('heading',name='04 人类核查',exact=True).count()==0
    page.get_by_role('combobox',name='故障案例',exact=True).click()
    page.get_by_role('option',name='bank-001',exact=True).click()
    expect(page.get_by_role('textbox',name='判断理由',exact=True)).to_have_value(review)
    report={'status':'passed','run_id':result['run_id'],'model_calls':result['calls'],
        'checks':['real UI analysis','raw evidence rendered','review bound to run','locale retains result and feedback without new analysis','case switch hides stale output','JSON export'],
        'human_review':'Automated test only; no user acceptance claimed.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)
    browser.close()
