from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManager
from django.template import loader, Context
from django.db.models import Count
from server.models import *
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import server.utils as utils

class DiskError(IPlugin):
    def show_widget(self, page, machines=None, theid=None):
        # The data is data is pulled from the database and passed to a template.
        
        # There are three possible views we're going to be rendering to - front, bu_dashbaord and group_dashboard. If page is set to bu_dashboard, or group_dashboard, you will be passed a business_unit or machine_group id to use (mainly for linking to the right search).
        if page == 'front':
            t = loader.get_template('diskerror/templates/front.html')
            if not machines:
                machines = Machine.objects.all()
        
        if page == 'bu_dashboard':
            t = loader.get_template('diskerror/templates/id.html')
            if not machines:
                machines = utils.getBUmachines(theid)
        
        if page == 'group_dashboard':
            t = loader.get_template('diskerror/templates/id.html')
            if not machines:
                machine_group = get_object_or_404(MachineGroup, pk=theid)
                machines = Machine.objects.filter(machine_group=machine_group)
        
        if machines:
            time_90days = datetime.now() - timedelta(days=90)
            time_30days = datetime.now() - timedelta(days=30)
            errors_90days = machines.filter(historicalfact__fact_name='diskerror', historicalfact__fact_data__gte=1, historicalfact__fact_recorded__gte=time_90days).distinct().count()
            errors_30days = machines.filter(historicalfact__fact_name='diskerror', historicalfact__fact_data__gte=1, historicalfact__fact_recorded__gte=time_30days).distinct().count()
        else:
            errors = None
    
        c = Context({
            'title': 'Disk Errors',
            'warnings': errors_90days,
            'errors': errors_30days,
            'page': page,
            'theid': theid
        })
        return t.render(c), 4
        
    def filter_machines(self, machines, data):
        if data == 'warnings':
            time_90days = datetime.now() - timedelta(days=90)
            machines = machines.filter(historicalfact__fact_name='diskerror', historicalfact__fact_data__gte=1, historicalfact__fact_recorded__gte=time_90days).distinct()
            title = 'Machines with recorded disk I/O errors in the past 90 days'
    
        elif data == 'errors':
            time_30days = datetime.now() - timedelta(days=30)
            machines = machines.filter(historicalfact__fact_name='diskerror', historicalfact__fact_data__gte=1, historicalfact__fact_recorded__gte=time_30days).distinct()
            title = 'Machines with recorded disk I/O errors in the past 30 days'
    
        else:
            machines = None
            title = 'Unknown'
    
        return machines, title
