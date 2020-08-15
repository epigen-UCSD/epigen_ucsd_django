from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'manager_app'
urlpatterns = [
    path('collab_list/', views.CollaboratorListView, name='collab_list'),
    path('collab_add/', views.CollaboratorCreateView, name='collab_add'),
    path('collab_group_account_add/', views.GroupAccountCreateView, name='group_account_add'),
    #path('index_add/', views.IndexCreateView, name='index_add'),
    path('collabinfo_add/', views.CollabInfoAddView, name='collabinfo_add'),
    path('ajax/load-groups/', views.load_groups, name='ajax_load_groups'),
    path('ajax/group_add/', views.AjaxGroupCreateView, name='ajax_group_add'),
    path('ajax/load-collabs/', views.load_collabs, name='ajax_load_collabs'),
    path('ajax/load-researchcontact/', views.load_researchcontact, name='ajax_load_researchcontact'),
    path('ajax/load-email/', views.load_email, name='ajax_load_email'),
    path('servicerequest_add/', views.ServiceRequestCreateView, name='collab_servicerequest_add'),
    #path('servicerequest_add/', views.ServiceRequestCreateView, name='quote_add'),
    path('servicerequest_update/<int:pk>/', views.ServiceRequestUpdateView, name='collab_servicerequest_update'),
    path('add_new_quote/<int:pk>/', views.ServiceRequestAddNewQuoteView, name='collab_servicerequest_add_new_quote'),
    path('servicerequests/', TemplateView.as_view(template_name="manager_app/servicerequests_list.html"), name='servicerequests_list'),
    path('servicerequests_list/', views.ServiceRequestDataView, name='service_request_display'),
    path('quote/<slug:quoteid>/', views.QuotePdfView, name='quote_pdf'),
    path('quote/<slug:quoteid>/text_update/', views.QuoteTextUpdateView, name='quote_text_update'),
    path('quote_add/', views.QuoteAddView, name='quote_add'),
    path('quotes/', TemplateView.as_view(template_name="manager_app/quotes_list.html"), name='quote_list'),
    path('quote_list/', views.QuoteListView, name='quote_display'),

]