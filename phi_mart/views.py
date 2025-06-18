from django.shortcuts import redirect

def api_root_view(reqeust):
    return redirect('api-root')