from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from data_taking_objects.models import Lumisection

from histograms.models import LumisectionHistogram1D, LumisectionHistogram2D
from .forms import QuickJumpForm

import data_taking_objects.views

import numpy as np
from urllib.parse import quote, unquote

# Create your views here.

@login_required
def visualize_histogram(request, runnr, lumisection, title_sanitised):
    """
    View for histogram file manager. Lists all available datafiles and their
    parsing status
    """

    if request.method == 'GET':
        form = QuickJumpForm(request.GET)
        if form.is_valid():
            runnr = form.cleaned_data["runnr"]
            lumisection = form.cleaned_data["lumisection"]
            title = form.cleaned_data["title"]
            title_sanitised = quote(title, safe='')
            return redirect("visualize_histogram:visualize_histogram",
                runnr=runnr, 
                lumisection=lumisection, 
                title_sanitised=title_sanitised
            )
        else: 
            form = QuickJumpForm(
                initial = {
                    "runnr": runnr,
                    "lumisection": lumisection,
                    "title": unquote(title_sanitised)
                }
            )
    else: 
        form = QuickJumpForm(
            initial = {
                "runnr": runnr,
                "lumisection": lumisection,
                "title": unquote(title_sanitised)
            }
        )

    try:
        title = unquote(title_sanitised)
        target_lumi = Lumisection.objects.get(run_id = runnr, ls_number = lumisection)
        lumi1d_searchresults = LumisectionHistogram1D.objects.filter(title=title, lumisection=target_lumi)
        lumi2d_searchresults = LumisectionHistogram2D.objects.filter(title=title, lumisection=target_lumi)
        if len(lumi1d_searchresults) == 1: 
            histobj = lumi1d_searchresults[0]
            hist_xmin_safe = histobj.x_min if histobj.x_min else 0
            hist_xmax_safe = histobj.x_max if histobj.x_max else histobj.x_bin
            return render(
                request,
                "visualize_histogram/visualize_histogram.html",
                {
                    "data": histobj.data,
                    "is2d": False,
                    "bins": np.linspace(hist_xmin_safe, hist_xmax_safe, histobj.x_bin+1).tolist(), 
                    "title": histobj.title,
                    "runnr": target_lumi.run_id,
                    "lumisection": target_lumi.ls_number,
                    "form": form
                }
            )
        elif len(lumi2d_searchresults) == 1: 
            histobj = lumi2d_searchresults[0]
            hist_xmin_safe = histobj.x_min if histobj.x_min else 0
            hist_xmax_safe = histobj.x_max if histobj.x_max else histobj.x_bin
            hist_ymin_safe = histobj.y_min if histobj.y_min else 0
            hist_ymax_safe = histobj.y_max if histobj.y_max else histobj.y_bin
            return render(
                request,
                "visualize_histogram/visualize_histogram.html",
                {
                    "data": histobj.data,
                    "is2d": True,
                    "xbins": np.linspace(hist_xmin_safe, hist_xmax_safe, histobj.x_bin+1).tolist(), 
                    "ybins": np.linspace(hist_ymin_safe, hist_ymax_safe, histobj.y_bin+1).tolist(), 
                    "title": histobj.title,
                    "runnr": target_lumi.run_id,
                    "lumisection": target_lumi.ls_number,
                    "form": form
                }
            )
        else: 
            return render(
                request,
                "visualize_histogram/visualize_histogram.html",
                {"data": None, "runnr": runnr, "lumisection": lumisection, "title": title, "form": form}
            )
    except (Lumisection.DoesNotExist):
        # Return with no context
        return render(
            request,
            "visualize_histogram/visualize_histogram.html",
            {"data": None, "runnr": runnr, "lumisection": lumisection, "title": title, "form": form}
        )
    
@login_required
def visualize_histogram_dummy(request):
    """
    View for histogram file manager. Lists all available datafiles and their
    parsing status
    """

    if request.method == 'GET':
        form = QuickJumpForm(request.GET)
        if form.is_valid():
            runnr = form.cleaned_data["runnr"]
            lumisection = form.cleaned_data["lumisection"]
            title_sanitised = quote(form.cleaned_data["title"], safe='')
            return redirect("visualize_histogram:visualize_histogram",
                runnr=runnr, 
                lumisection=lumisection, 
                title_sanitised=title_sanitised
            )
        else: form = QuickJumpForm()
    else:
        form = QuickJumpForm()

    # dummy_hist = LumisectionHistogram1D.objects.latest("lumisection_id")
    # return redirect("visualize_histogram:visualize_histogram", runnr=dummy_hist.lumisection.run_id, 
    #     lumisection=dummy_hist.lumisection.ls_number, 
    #     title=dummy_hist.title
    # )
    print(request.GET)
    return render(request, "visualize_histogram/visualize_firstpage.html", {"form": form})

@login_required
def redirect_lumisection(request, runnr, lumisection):
    """
    View for histogram file manager. Lists all available datafiles and their
    parsing status
    """

    return data_taking_objects.views.lumisection_view(request, runnr, lumisection)

@login_required
def redirect_run(request, runnr):
    """
    View for histogram file manager. Lists all available datafiles and their
    parsing status
    """

    return data_taking_objects.views.run_view(request, runnr)