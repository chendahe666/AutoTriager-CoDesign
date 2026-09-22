def record_review(result,decision,reason):
    if decision not in ('accept','reject','unresolved'): raise ValueError('Invalid judgment')
    if not reason.strip(): raise ValueError('A reason is required')
    return {'run_id':result['run_id'],'case_id':result['case_id'],'decision':decision,'reason':reason.strip()}

def visible_result(results,case_id):
    result=results.get(case_id)
    return result if result and result['case_id']==case_id else None
