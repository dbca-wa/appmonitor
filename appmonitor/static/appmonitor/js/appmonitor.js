var appmonitor = {
    var: {
        loader: '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>',
        edit_monitor_access: false
    },
    init: function() {
        appmonitor.get_checks();
        appmonitor.var.edit_monitor_access = $('#edit_access_monitoring').val();

        $("#new_monitoring_btn" ).on( "click", function() { 


            $('#new-monitoring-operator-div').hide(); 
            $('#new-monitoring-url-div').hide();
            $('#new-monitoring-stringcheck-div').hide();
            $('#new-monitoring-jsonkey-div').hide();
            $('#new-monitoring-statuscode-div').hide();
            $('#new-monitoring-host-div').hide();
            $('#new-monitoring-port-div').hide();
            $('#new-monitoring-ignoressl-div').hide();
            $('#new-monitoring-sharepointurl-div').hide();
            $('#new-monitoring-sharepointusername-div').hide();
            $('#new-monitoring-sharepointpassword-div').hide();

            $('#new-monitoring-basicauth-div').hide();
            $('#new-monitoring-basic-auth-user-pass').hide();
            $('#new-monitoring-up-div').hide();
            $('#new-monitoring-warn-div').hide();
            $('#new-monitoring-down-div').hide();


            $('#new-monitoring-checkname').val("");         
            $('#new-monitoring-systemid').val("");
            $('#new-monitoring-montype').val(""); 
            $('#new-monitoring-responsiblegroup').val(""); 

            $('#new-monitoring-operator').val(""); 
            $('#new-monitoring-url').val(""); 
            $('#new-monitoring-stringcheck').val(""); 
            $('#new-monitoring-jsonkey').val(""); 
            $('#new-monitoring-statuscode').val(""); 
            $('#new-monitoring-host').val(""); 
            $('#new-monitoring-port').val(""); 
            $('#new-monitoring-ignoressl').prop( "checked", false );
            $('#new-monitoring-sharepointurl').val("");
            $('#new-monitoring-sharepointusername').val("");
            $('#new-monitoring-sharepointpassword').val("");
            $('#new-monitoring-basicauth').prop( "checked", false );
            $('#new-monitoring-username').val("");
            $('#new-monitoring-password').val("");            
            $('#new-monitoring-up').val(""); 
            $('#new-monitoring-warn').val(""); 
            $('#new-monitoring-down').val("");
            $("#new-monitoring-active").prop( "checked", true );
                    
            $('#NewMonitorModal').modal('show');
        });
        $("#edit-monitoring-montype" ).on( "change", function() { 
            var value = this.value;
            appmonitor.mon_type_load(value,'edit');
        });

        $("#new-monitoring-montype" ).on( "change", function() { 
            var value = this.value;
            appmonitor.mon_type_load(value,'new');    
        });
        $("#create-monitoring-btn" ).on( "click", function() { 
            appmonitor.save_monitoring('new');
        });
        $( "#save-monitoring-btn" ).on( "click", function() {
            appmonitor.save_monitoring("save");           
        });  
    },
    mon_type_load: function(value,save_type) {
        
        appmonitor.reset_new_monitoring_form(save_type);

        if (value == 1) {            
            $('#'+save_type+'-monitoring-url-div').show();
            $('#'+save_type+'-monitoring-stringcheck-div').show();
            $('#'+save_type+'-monitoring-ignoressl-div').hide();

            $('#'+save_type+'-monitoring-basicauth-div').show();
            $('#'+save_type+'-monitoring-basic-auth-user-pass').show();
        }
        if (value == 2) {
            
            $('#'+save_type+'-monitoring-host-div').show();
        }
        if (value == 3) {
            $('#'+save_type+'-monitoring-host-div').show();
            $('#'+save_type+'-monitoring-port-div').show();           
        }
        if (value == 5) {           
            $('#'+save_type+'-monitoring-host-div').show();           
        }

        if (value == 8) {         
            $('#'+save_type+'-monitoring-url-div').show();
            $('#'+save_type+'-monitoring-operator-div').show(); 
            $('#'+save_type+'-monitoring-jsonkey-div').show();

            $('#'+save_type+'-monitoring-up-div').show();
            $('#'+save_type+'-monitoring-warn-div').show();
            $('#'+save_type+'-monitoring-down-div').show();

            $('#'+save_type+'-monitoring-basicauth-div').show();
            $('#'+save_type+'-monitoring-basic-auth-user-pass').show();
                     
        } 

        if (value == 9) {         
            $('#'+save_type+'-monitoring-url-div').show();  
            $('#'+save_type+'-monitoring-statuscode-div').show();

            $('#'+save_type+'-monitoring-basicauth-div').hide();
            $('#'+save_type+'-monitoring-basic-auth-user-pass').hide();
            
        } 
        if (value == 10) {         
            $('#'+save_type+'-monitoring-sharepointurl-div').show();
            $('#'+save_type+'-monitoring-sharepointusername-div').show();
            $('#'+save_type+'-monitoring-sharepointpassword-div').show();   
            
        }  

    },
    reset_new_monitoring_form: function(save_type) {
        
        // $('#'+save_type+'-monitoring-checkname').val("");
        
        // $('#'+save_type+'-monitoring-systemid').val("");
        $('#'+save_type+'-monitoring-operator-div').hide(); 
        $('#'+save_type+'-monitoring-url-div').hide();
        $('#'+save_type+'-monitoring-stringcheck-div').hide();
        $('#'+save_type+'-monitoring-jsonkey-div').hide();
        $('#'+save_type+'-monitoring-statuscode-div').hide();
        $('#'+save_type+'-monitoring-host-div').hide();
        $('#'+save_type+'-monitoring-port-div').hide();
        $('#'+save_type+'-monitoring-ignoressl-div').hide();
        $('#'+save_type+'-monitoring-sharepointurl-div').hide();
        $('#'+save_type+'-monitoring-sharepointusername-div').hide();
        $('#'+save_type+'-monitoring-sharepointpassword-div').hide();   
        $('#'+save_type+'-monitoring-basicauth-div').hide();
        $('#'+save_type+'-monitoring-basic-auth-user-pass').hide();
        $('#'+save_type+'-monitoring-up-div').hide();
        $('#'+save_type+'-monitoring-warn-div').hide();
        $('#'+save_type+'-monitoring-down-div').hide();
    },
    save_monitoring: function(save_type) {
        
        var save_url = '/api/monitor/create';
        var messages_class = 'new';

        var monitor_id = null;
        if (save_type == 'save') {
            messages_class  = 'edit';
            save_url = '/api/monitor/update'
            monitor_id = $('#edit-monitoring-id').val();
        }
        
        var csrf_token = $("#csrfmiddlewaretoken").val();

        var checkname = $('#'+messages_class+'-monitoring-checkname').val(); 
        var montype = $('#'+messages_class+'-monitoring-montype').val(); 
        var systemid = $('#'+messages_class+'-monitoring-systemid').val(); 
        var responsiblegroup = $('#'+messages_class+'-monitoring-responsiblegroup').val(); 
        var operator = $('#'+messages_class+'-monitoring-operator').val(); 
        var url = $('#'+messages_class+'-monitoring-url').val(); 
        var stringcheck = $('#'+messages_class+'-monitoring-stringcheck').val(); 
        var jsonkey = $('#'+messages_class+'-monitoring-jsonkey').val(); 
        var statuscode = $('#'+messages_class+'-monitoring-statuscode').val(); 
        var host = $('#'+messages_class+'-monitoring-host').val(); 
        var port = $('#'+messages_class+'-monitoring-port').val(); ;
        var ignoressl = $('#'+messages_class+'-monitoring-ignoressl').prop('checked');
        var sharepointurl = $('#new-monitoring-sharepointurl').val("");
        var sharepointusername = $('#new-monitoring-sharepointusername').val("");
        var sharepointpassword = $('#new-monitoring-sharepointpassword').val("");
        var basicauth = $('#'+messages_class+'-monitoring-basicauth').prop('checked');
        var username = $('#new-monitoring-username').val("");
        var password = $('#new-monitoring-password').val("");
        var up = $('#'+messages_class+'-monitoring-up').val(); 
        var warn = $('#'+messages_class+'-monitoring-warn').val(); 
        var down = $('#'+messages_class+'-monitoring-down').val();
        var active = $('#'+messages_class+'-monitoring-active').prop('checked');

        var json_data = {   'monitor_id' : monitor_id,
                            'checkname' : checkname, 
                            'montype' : montype,
                            'systemid' : systemid,
                            'responsiblegroup':responsiblegroup, 
                            'operator':operator, 
                            'url': url,
                            'stringcheck' :stringcheck,
                            'jsonkey' : jsonkey,
                            'statuscode' : statuscode,
                            'host' : host,
                            'port' : port,
                            'ignoressl' : ignoressl,
                            'sharepointurl' : sharepointurl,
                            'sharepointusername' : sharepointusername,
                            'sharepointpassword' : sharepointpassword,
                            'basicauth' : basicauth,
                            'username' : username,
                            'password' : password,
                            'up' : up,
                            'warn' : warn,
                            'down' : down,
                            'active' : active
                        }

        $.ajax({
            url: save_url,
            type: 'POST',
            data: JSON.stringify(json_data),
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                appmonitor.get_checks();
                if (save_type == 'save') {
                    $('#EditMonitorModal').modal('hide');
                } else {
                    $('#NewMonitorModal').modal('hide');
                }                
            },
            error: function (error) {
                alert('error saving platform.')
            },
        });

    },
    get_update_monitor_by_id: function(pid) {

        $.ajax({
            type: "GET",
            url: "/api/monitor/"+pid,
            data: {},
            error: function(resp) {
                $('#monitorlist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');
            },
            success: function (resp) {
                console.log(resp);
                var htmlval = "";
                if (resp != null) {

                    var messages_class = 'edit';
                    $('#edit-monitor-error').text();
                    $('#edit-monitor-error').hide();
                    $('#edit-monitor-success').text("");
                    $('#edit-monitor-success').hide();   
                    appmonitor.mon_type_load(resp.monitor_info_array.mon_type,'edit');

                    $('#edit-monitoring-id-label').html(resp.monitor_info_array.id);
                    $('#edit-monitoring-id').val(resp.monitor_info_array.id);

                    $('#'+messages_class+'-monitoring-checkname').val(resp.monitor_info_array.check_name); 
                    $('#'+messages_class+'-monitoring-montype').val(resp.monitor_info_array.mon_type); 
                    $('#'+messages_class+'-monitoring-systemid').val(resp.monitor_info_array.system_id); 
                    $('#'+messages_class+'-monitoring-responsiblegroup').val(resp.monitor_info_array.group_responsible_id); 
                    $('#'+messages_class+'-monitoring-operator').val(resp.monitor_info_array.check_operator); 
                    $('#'+messages_class+'-monitoring-url').val(resp.monitor_info_array.url); 
                    $('#'+messages_class+'-monitoring-stringcheck').val(resp.monitor_info_array.string_check); 
                    $('#'+messages_class+'-monitoring-jsonkey').val(resp.monitor_info_array.json_key); 
                    $('#'+messages_class+'-monitoring-statuscode').val(resp.monitor_info_array.status_code); 
                    $('#'+messages_class+'-monitoring-host').val(resp.monitor_info_array.host); 
                    $('#'+messages_class+'-monitoring-port').val(resp.monitor_info_array.port); 
                    if (resp.monitor_info_array.ignore_ssl_verification == true) { 
                        $('#'+messages_class+'-monitoring-ignoressl').prop('checked', true);
                    } else {
                        $('#'+messages_class+'-monitoring-ignoressl').prop('checked', false);
                    }
                    $('#new-monitoring-sharepointurl').val(resp.monitor_info_array.sharepoint_url);
                    $('#new-monitoring-sharepointusername').val(resp.monitor_info_array.sharepoint_username);
                    $('#new-monitoring-sharepointpassword').val(resp.monitor_info_array.sharepoint_password);
                    
                    if (resp.monitor_info_array.use_basic_auth == true) {
                        $('#'+messages_class+'-monitoring-basicauth').prop('checked', true);
                    } else {
                        $('#'+messages_class+'-monitoring-basicauth').prop('checked', false);
                    }
                    $('#new-monitoring-username').val(resp.monitor_info_array.username);
                    $('#new-monitoring-password').val(resp.monitor_info_array.password);
                    $('#'+messages_class+'-monitoring-up').val(resp.monitor_info_array.up_value); 
                    $('#'+messages_class+'-monitoring-warn').val(resp.monitor_info_array.warn_value); 
                    $('#'+messages_class+'-monitoring-down').val(resp.monitor_info_array.down_value);
                    $('#'+messages_class+'-monitoring-active').prop('checked');
                    if (resp.monitor_info_array.active == true) {
                        $('#'+messages_class+'-monitoring-active').prop('checked', true);
                    } else {
                        $('#'+messages_class+'-monitoring-active').prop('checked', false);
                    }


                    
                }
            }
        });      

    },
    get_checks: function() {

        // $('#sensorlist-tbody').html("<tr><td colspan='5' class='text-center'>"+appmonitor.var.loader+"</td></tr>");
        $('#loading-progress').html(appmonitor.var.loader);
        $.ajax({
            type: "post",
            url: "/api/get-checks/",
            data: {},
            error: function(resp) {
                $('#sensorlist-tbody').html('<tr><td colspan="5" class="text-center">No Results</td></tr>');
            },
            success: function (resp) {
                var htmlval = "";
                if (resp != null) {
                    if (resp.monitors.length > 0) {
                        // for (let i = 0; i < resp.monitors.length; i++) {
                        //     htmlval+= "<tr>";                                                                         
                        //     htmlval+= "     <td>";                            
                        //     if (resp.monitors[i].status == 0 ) {
                        //         htmlval+= "<div class='bg-secondary status-box-white' style='font-size: 10px; padding-top: 7px;'>UNKNOWN</div>";
                        //     } else if (resp.monitors[i].status == 1 ) {
                        //         htmlval+= "<div class='bg-danger status-box-white' >DOWN</div>";
                        //     } else if (resp.monitors[i].status == 2 ) {
                        //         htmlval+= "<div class='bg-warning status-box-white' >WARN</div>";
                        //     } else if (resp.monitors[i].status == 3 ) {
                        //         htmlval+= "<div class='bg-success status-box-white' >UP</div>";
                        //     }
                        //     htmlval+= "     </td>";
                        //     //htmlval+= "     <td>"+resp.monitors[i].id+"</td>";
                        //     htmlval+= "     <td><a href='"+resp.monitors[i].it_system_register_url+"'>"+resp.monitors[i].system_id+"</a></td>";                            
                        //     htmlval+= "     <td>"+resp.monitors[i].name;
                        //     if (resp.monitors[i].url != null) {
                        //         if (resp.monitors[i].url.length > 0 ) {
                        //             htmlval+= "     &nbsp;<a href='"+resp.monitors[i].url+"' target='urlmonitor_"+resp.monitors[i].id+"'><i class='bi bi-box-arrow-up-right' style='color: blue; cursor:pointer;'></i></a>";
                        //         }
                        //     }
                        //     htmlval+= "     </td>";      
                        //     htmlval+= "     <td>"+resp.monitors[i].mon_type+"</td>";
                        //     htmlval+= "     <td>"+resp.monitors[i].responsible_group+"</td>";
                            
                        //     htmlval+= "     <td>"+resp.monitors[i].last_check_date+"</td>";
                        //     htmlval+= "     <td><a class='btn btn-primary btn-sm' href='/monitor/history/"+resp.monitors[i].id+"/'>History</a></td>";
                        //     htmlval+= "</tr>";

                        // }

                  


                        for (let i = 0; i < resp.monitors.length; i++) {
                            button_json = '{"id": "'+resp.monitors[i].id+'"}'
                            if (resp.monitors[i].status == 0 ) {
                                
                                htmlval+= "<tr>";                                                                         
                                htmlval+= "     <td>";                            
                                
                                    htmlval+= "<div class='bg-secondary status-box-white' style='font-size: 10px; padding-top: 7px;'>UNKNOWN</div>";
                                
                                htmlval+= "     </td>";
                                //htmlval+= "     <td>"+resp.monitors[i].id+"</td>";
                                htmlval+= "     <td><a href='"+resp.monitors[i].it_system_register_url+"'>"+resp.monitors[i].system_id+"</a></td>";                            
                                htmlval+= "     <td>"+resp.monitors[i].name;
                                if (resp.monitors[i].url != null) {
                                    if (resp.monitors[i].url.length > 0 ) {
                                        htmlval+= "     &nbsp;<a href='"+resp.monitors[i].url+"' target='urlmonitor_"+resp.monitors[i].id+"'><i class='bi bi-box-arrow-up-right' style='color: blue; cursor:pointer;'></i></a>";
                                    }
                                }
                                htmlval+= "     </td>";      
                                htmlval+= "     <td>"+resp.monitors[i].mon_type+"</td>";
                                htmlval+= "     <td>"+resp.monitors[i].responsible_group+"</td>";
                                
                                htmlval+= "     <td>"+resp.monitors[i].last_check_date+"</td>";
                                htmlval+= "     <td>";
                                if (appmonitor.var.edit_monitor_access == 'True') {
                                    htmlval+= "     <button class='btn btn-primary btn-sm monitor-edit-btn' id='monitor-edit-btn-"+resp.monitors[i].id+"' data-json='"+button_json+"' >Edit</button>";
                                }
                                htmlval+= "     <a class='btn btn-primary btn-sm' href='/monitor/history/"+resp.monitors[i].id+"/'>History</a>";
                                htmlval+= "     </td>";
                                htmlval+= "</tr>";
                            }
                        }

                        for (let i = 0; i < resp.monitors.length; i++) {
                            if (resp.monitors[i].status == 1 ) {
                                htmlval+= "<tr>";                                                                         
                                htmlval+= "     <td>";                            
                                
                                htmlval+= "<div class='bg-danger status-box-white' >DOWN</div>";
                                
                                htmlval+= "     </td>";
                                //htmlval+= "     <td>"+resp.monitors[i].id+"</td>";
                                htmlval+= "     <td><a href='"+resp.monitors[i].it_system_register_url+"'>"+resp.monitors[i].system_id+"</a></td>";                            
                                htmlval+= "     <td>"+resp.monitors[i].name;
                                if (resp.monitors[i].url != null) {
                                    if (resp.monitors[i].url.length > 0 ) {
                                        htmlval+= "     &nbsp;<a href='"+resp.monitors[i].url+"' target='urlmonitor_"+resp.monitors[i].id+"'><i class='bi bi-box-arrow-up-right' style='color: blue; cursor:pointer;'></i></a>";
                                    }
                                }
                                htmlval+= "     </td>";      
                                htmlval+= "     <td>"+resp.monitors[i].mon_type+"</td>";
                                htmlval+= "     <td>"+resp.monitors[i].responsible_group+"</td>";
                                
                                htmlval+= "     <td>"+resp.monitors[i].last_check_date+"</td>";
                                htmlval+= "     <td>";
                                if (appmonitor.var.edit_monitor_access == 'True') {
                                    htmlval+= "     <button class='btn btn-primary btn-sm monitor-edit-btn' id='monitor-edit-btn-"+resp.monitors[i].id+"' data-json='"+button_json+"' >Edit</button>";
                                }
                                htmlval+= "         <a class='btn btn-primary btn-sm' href='/monitor/history/"+resp.monitors[i].id+"/'>History</a>";
                                htmlval+= "     </td>";
                                htmlval+= "</tr>";
                            }

                        }

                        for (let i = 0; i < resp.monitors.length; i++) {
                            if (resp.monitors[i].status == 2 ) {
                                htmlval+= "<tr>";                                                                         
                                htmlval+= "     <td>";                            
                                
                                htmlval+= "<div class='bg-warning status-box-white' >WARN</div>";
                                
                                htmlval+= "     </td>";
                                //htmlval+= "     <td>"+resp.monitors[i].id+"</td>";
                                htmlval+= "     <td><a href='"+resp.monitors[i].it_system_register_url+"'>"+resp.monitors[i].system_id+"</a></td>";                            
                                htmlval+= "     <td>"+resp.monitors[i].name;
                                if (resp.monitors[i].url != null) {
                                    if (resp.monitors[i].url.length > 0 ) {
                                        htmlval+= "     &nbsp;<a href='"+resp.monitors[i].url+"' target='urlmonitor_"+resp.monitors[i].id+"'><i class='bi bi-box-arrow-up-right' style='color: blue; cursor:pointer;'></i></a>";
                                    }
                                }
                                htmlval+= "     </td>";      
                                htmlval+= "     <td>"+resp.monitors[i].mon_type+"</td>";
                                htmlval+= "     <td>"+resp.monitors[i].responsible_group+"</td>";
                                
                                htmlval+= "     <td>"+resp.monitors[i].last_check_date+"</td>";
                                htmlval+= "     <td>";
                                if (appmonitor.var.edit_monitor_access == 'True') {
                                    htmlval+= "     <button class='btn btn-primary btn-sm monitor-edit-btn' id='monitor-edit-btn-"+resp.monitors[i].id+"' data-json='"+button_json+"' >Edit</button>";
                                }                                
                                htmlval+= "     <a class='btn btn-primary btn-sm' href='/monitor/history/"+resp.monitors[i].id+"/'>History</a>";
                                htmlval+= "     </td>";
                                htmlval+= "</tr>";
                            }

                        }

                        for (let i = 0; i < resp.monitors.length; i++) {
                            if (resp.monitors[i].status == 3 ) {
                                htmlval+= "<tr>";                                                                         
                                htmlval+= "     <td>";                            
                                
                                htmlval+= "<div class='bg-success status-box-white' >UP</div>";
                                
                                htmlval+= "     </td>";
                                //htmlval+= "     <td>"+resp.monitors[i].id+"</td>";
                                htmlval+= "     <td><a href='"+resp.monitors[i].it_system_register_url+"'>"+resp.monitors[i].system_id+"</a></td>";                            
                                htmlval+= "     <td>"+resp.monitors[i].name;
                                if (resp.monitors[i].url != null) {
                                    if (resp.monitors[i].url.length > 0 ) {
                                        htmlval+= "     &nbsp;<a href='"+resp.monitors[i].url+"' target='urlmonitor_"+resp.monitors[i].id+"'><i class='bi bi-box-arrow-up-right' style='color: blue; cursor:pointer;'></i></a>";
                                    }
                                }
                                htmlval+= "     </td>";      
                                htmlval+= "     <td>"+resp.monitors[i].mon_type+"</td>";
                                htmlval+= "     <td>"+resp.monitors[i].responsible_group+"</td>";
                                
                                htmlval+= "     <td>"+resp.monitors[i].last_check_date+"</td>";
                                htmlval+= "     <td>";
                                if (appmonitor.var.edit_monitor_access == 'True') {
                                    htmlval+= "     <button class='btn btn-primary btn-sm monitor-edit-btn' id='monitor-edit-btn-"+resp.monitors[i].id+"' data-json='"+button_json+"' >Edit</button>";
                                }
                                htmlval+= "     <a class='btn btn-primary btn-sm' href='/monitor/history/"+resp.monitors[i].id+"/'>History</a>";
                                htmlval+= "</td>";
                                htmlval+= "</tr>";
                            }

                        }                        

                        $('#sensorlist-tbody').html(htmlval);
                        $(".monitor-edit-btn").on( "click", function() {
                            var btndata_json = $(this).attr('data-json');
                            var btndata = JSON.parse(btndata_json);
                            
                            appmonitor.get_update_monitor_by_id(btndata['id'])
                            // appmonitor_platform.edit_platform();
                            
                            $("#EditMonitorModal").modal("show");
                                     
                        });
                        $('#total-unknown').html(resp.monitor_status_total[0]);
                        $('#total-down').html(resp.monitor_status_total[1]);
                        $('#total-warn').html(resp.monitor_status_total[2]);
                        $('#total-up').html(resp.monitor_status_total[3]);
                        $('#current-server-time').html(resp.monitor_status['current_time']);
                        $('#last-job-run-time').html(resp.monitor_status['last_job_run']);
                        
                    } else {
                        $('#sensorlist-tbody').html('<tr><td colspan="5" class="text-center">No Results</td></tr>');                    
                    }   
                    $('#loading-progress').html(""); 
                    setTimeout("appmonitor.get_checks()", 30000)                      
                } else {
                    $('#sensorlist-tbody').html('<tr><td colspan="5" class="text-center">No Results</td></tr>');
                    $('#loading-progress').html("");
                }
                
            }
        })        
    }
}
