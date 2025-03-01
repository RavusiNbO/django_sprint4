from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


class AboutTemplateView(TemplateView):
    template_name = "pages/about.html"


class RulesTemplateView(TemplateView):
    template_name = "pages/rules.html"


def page_not_found(request, exception):
    return render(request, "pages/404.html", status=404)


def forbidden(request, exception, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def server_error(request):
    return render(request, "pages/500.html", status=500)
