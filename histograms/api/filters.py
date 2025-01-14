import django_filters
from django import forms
from histograms.models import (
    RunHistogram,
    LumisectionHistogram1D,
    LumisectionHistogram2D,
)


class InFilter(django_filters.filters.BaseInFilter, django_filters.filters.CharFilter):
    pass


class RunHistogramFilter(django_filters.rest_framework.FilterSet):

    title = django_filters.filters.AllValuesMultipleFilter(
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control",
                "size": "10",
            }
        )
    )

    primary_dataset = django_filters.AllValuesFilter(
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        )
    )

    run__run_number__in = InFilter(field_name="run__run_number", lookup_expr="in")

    source_data_file__filepath__contains = django_filters.CharFilter(
        field_name="source_data_file__filepath", lookup_expr="icontains"
    )

    class Meta:
        model = RunHistogram
        fields = {
            "run__run_number": ["gte", "lte", "exact"],
            "entries": [
                "gte",
                "lte",
            ],
            "mean": [
                "exact",
                "gte",
                "lte",
            ],
            "rms": [
                "exact",
                "gte",
                "lte",
            ],
            "skewness": [
                "exact",
                "gte",
                "lte",
            ],
            "kurtosis": [
                "exact",
                "gte",
                "lte",
            ],
            "source_data_file": ["exact"],
        }


class LumisectionHistogram1DFilter(django_filters.FilterSet):

    title = django_filters.filters.AllValuesMultipleFilter(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "size": "10",
            }
        )
    )

    lumisection__ls_number__in = InFilter(
        field_name="lumisection__ls_number", lookup_expr="in"
    )
    lumisection__run__run_number__in = InFilter(
        field_name="lumisection__run__run_number", lookup_expr="in"
    )
    source_data_file__filepath__contains = django_filters.CharFilter(
        field_name="source_data_file__filepath", lookup_expr="icontains"
    )

    class Meta:
        model = LumisectionHistogram1D
        fields = {
            "lumisection__run__run_number": [
                "exact",
                "gte",
                "lte",
            ],
            "lumisection__ls_number": [
                "exact",
                "gte",
                "lte",
            ],
            "entries": [
                "gte",
                "lte",
            ],
            "source_data_file": ["exact"],
        }


class LumisectionHistogram2DFilter(django_filters.FilterSet):

    title = django_filters.filters.AllValuesMultipleFilter(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "size": "10",
            }
        )
    )

    lumisection__ls_number__in = InFilter(
        field_name="lumisection__ls_number", lookup_expr="in"
    )
    lumisection__run__run_number__in = InFilter(
        field_name="lumisection__run__run_number", lookup_expr="in"
    )
    source_data_file__filepath__contains = django_filters.CharFilter(
        field_name="source_data_file__filepath", lookup_expr="icontains"
    )

    class Meta:
        model = LumisectionHistogram2D
        fields = {
            "lumisection__run__run_number": [
                "exact",
                "gte",
                "lte",
            ],
            "lumisection__ls_number": [
                "exact",
                "gte",
                "lte",
            ],
            "entries": [
                "gte",
                "lte",
            ],
            "source_data_file": ["exact"],
        }
