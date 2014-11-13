from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManager
from django.template import loader, Context
from django.db.models import Count
from server.models import *
from django.shortcuts import get_object_or_404
import server.utils as utils
import time

class TimeMachine(IPlugin):
    def show_widget(self, page, machines=None, theid=None):
        # The data is data is pulled from the database and passed to a template.
        
        # There are three possible views we're going to be rendering to - front, bu_dashbaord and group_dashboard. If page is set to bu_dashboard, or group_dashboard, you will be passed a business_unit or machine_group id to use (mainly for linking to the right search).
        if page == 'front':
            t = loader.get_template('timemachine/templates/front.html')
            if not machines:
                machines = Machine.objects.all()
        
        if page == 'bu_dashboard':
            t = loader.get_template('timemachine/templates/id.html')
            if not machines:
                machines = utils.getBUmachines(theid)
        
        if page == 'group_dashboard':
            t = loader.get_template('timemachine/templates/id.html')
            if not machines:
                machine_group = get_object_or_404(MachineGroup, pk=theid)
                machines = Machine.objects.filter(machine_group=machine_group)
        
        if machines:
            time_week = int(time.time() - (86400 * 7))
            time_month = int(time.time() - (86400 * 28))

            tm_configured = machines.filter(fact__fact_name='timemachine_configured', fact__fact_data=1).count()
            tm_notconfigured = machines.filter(fact__fact_name='timemachine_configured', fact__fact_data=0).count()
            tm_recent_ok = machines.filter(fact__fact_name='timemachine_lastsnapshot', fact__fact_data__gte=time_week).count()
            tm_recent_warning = machines.filter(fact__fact_name='timemachine_lastsnapshot', fact__fact_data__lt=time_week, fact__fact_data__gte=time_month).count()
            tm_recent_error = machines.filter(fact__fact_name='timemachine_lastsnapshot', fact__fact_data__lt=time_month).count()
            tm_recent_error += machines.filter(fact__fact_name='timemachine_configured', fact__fact_data=1).exclude(fact__fact_name='timemachine_lastsnapshot').count()
        else:
            tm_configured = None
            tm_notconfigured = None
            tm_recent_ok = None
            tm_recent_warning = None
            tm_recent_error = None

        c = Context({
            'title': 'Time Machine',
            'tm_configured': tm_configured,
            'tm_notconfigured': tm_notconfigured,
            'tm_recent_ok': tm_recent_ok,
            'tm_recent_warning': tm_recent_warning,
            'tm_recent_error': tm_recent_error,
            'theid': theid,
            'page': page
        })
        return t.render(c), 4
    
    def filter_machines(self, machines, data):
        # You will be passed a QuerySet of machines, you then need to perform some filtering based on the 'data' part of the url from the show_widget output. Just return your filtered list of machines and the page title.
        time_week = int(time.time() - (86400 * 7))
        time_month = int(time.time() - (86400 * 28))

        if data == 'configured':
            machines = machines.filter(fact__fact_name='timemachine_configured', fact__fact_data=1)
            title = 'Machines configured for Time Machine'
        elif data == 'notconfigured':
            machines = machines.filter(fact__fact_name='timemachine_configured', fact__fact_data=0)
            title = 'Machines not configured for Time Machine'
        elif data == 'recent_ok':
            machines = machines.filter(fact__fact_name='timemachine_lastsnapshot', fact__fact_data__gte=time_week)
            title = 'Machines backed up in last 7 days'
        elif data == 'recent_warning':
            machines = machines.filter(fact__fact_name='timemachine_lastsnapshot', fact__fact_data__lt=time_week, fact__fact_data__gte=time_month)
            title = 'Machines backed up between 8 and 28 days ago'
        elif data == 'recent_error':
            setA = machines.filter(fact__fact_name='timemachine_lastsnapshot', fact__fact_data__lt=time_month)
            setB = machines.filter(fact__fact_name='timemachine_configured', fact__fact_data=1).exclude(fact__fact_name='timemachine_lastsnapshot')
            machines = setA | setB
            title = 'Machines backed up more than 28 days ago'
        else:
            machines = None
            title = 'Unknown'
        
        return machines, title    
