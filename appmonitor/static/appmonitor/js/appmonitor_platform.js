var appmonitor_platform = {
    var: {
        loader: '<button class="btn btn-primary" type="button" disabled><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Please Wait Loading...</button>',
        loader_old: '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>',
        edit_access: false
    },
    init: function() {
        appmonitor_platform.get_platforms(false);
        appmonitor_platform.var.edit_platform_access = $('#edit_platform_access').val();
        
        $( "#new_platform_btn" ).on( "click", function() {
            $('#new-platform-error').text("");
            $('#new-platform-error').hide();
            $('#new-platform-success').text("");
            $('#new-platform-success').hide();

            $('#new-platform-systemname').val("");
            $('#new-platform-apikey').val(appmonitor_platform.generateId().toUpperCase());
            $('#new-platform-responsiblegroup').val("");
            $("#new-platform-stalepackage").prop( "checked", true );
            $("#new-platform-active").prop( "checked", true );
            $('#NewPlatformModal').modal('show');
            
        });

        $( "#create-platform-btn" ).on( "click", function() {
            appmonitor_platform.save_platform("create");           
        });  
        $( "#save-platform-btn" ).on( "click", function() {
            appmonitor_platform.save_platform("save");           
        });

        $("#platform-responsiblegroup-monitor" ).on( "change", function() { 
            appmonitor_platform.get_platforms(true);
        });
        $("#platform-inactive-monitor" ).on( "change", function() { 
            appmonitor_platform.get_platforms(true);
        });
        $("#platform-keyword-monitor" ).on( "keyup", function() { 
                        
            appmonitor_platform.get_platforms(true);
            
        });           
        
    },
    save_platform: function(save_type) {
        save_url = '/api/platform/create';
        messages_class = 'new';
       
        var platform_id = null;
        if (save_type == 'save') {
            messages_class  = 'edit';
            save_url = '/api/platform/update'
            platform_id = $('#edit-platform-id').val();
        }

        var csrf_token = $("#csrfmiddlewaretoken").val();
        var platform_systemname = $('#'+messages_class+'-platform-systemname').val();
        var platform_apikey = $('#'+messages_class+'-platform-apikey').val();
        var platform_responsiblegroup = $('#'+messages_class+'-platform-responsiblegroup').val();
        var platform_stalepackage = $('#'+messages_class+'-platform-stalepackage').prop('checked');
        var platform_active = $('#'+messages_class+'-platform-active').prop('checked');

       
        if (platform_systemname.length > 7) { 
            // Continue toward saving data
        } else {
            $('#'+messages_class+'-platform-error').text("Please enter a valid system name 8-150 characters");
            $('#'+messages_class+'-platform-error').show();
            return;
        }
       
        if ((platform_apikey == 0) || (platform_apikey.length > 99)) {

        } else {
            $('#'+messages_class+'-platform-error').text("Minimum API key length is 100");
            $('#'+messages_class+'-platform-error').show();
            return;
        }

        if (platform_responsiblegroup > 0) { 
            // Continue toward saving data
        } else {
            $('#'+messages_class+'-platform-error').text("Please select an option for Group Responsible.");
            $('#'+messages_class+'-platform-error').show();
            return;
        }
        
        $.ajax({
            url: save_url,
            type: 'POST',
            data: JSON.stringify({'platform_id' : platform_id, 'platform_systemname':platform_systemname, 'platform_apikey':platform_apikey, 'platform_responsiblegroup': platform_responsiblegroup,"platform_stalepackage": platform_stalepackage, "platform_active": platform_active}),
            headers: {'X-CSRFToken' : csrf_token},
            contentType: 'application/json',
            success: function (response) {
                appmonitor_platform.get_platforms(true);
                if (save_type == 'save') {
                    $('#EditPlatformModal').modal('hide');
                } else {
                    $('#NewPlatformModal').modal('hide');
                }
                
            },
            error: function (error) {
                alert('error saving platform.')
            },
        });
        
    },
    edit_platform: function() {        
        alert('test');
    },
    get_update_platform_by_id: function(pid) {

        $.ajax({
            type: "GET",
            url: "/api/platform/"+pid,
            data: {},
            error: function(resp) {
                $('#platformlist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');
            },
            success: function (resp) {
                console.log(resp);
                var htmlval = "";
                if (resp != null) {
                    $('#edit-platform-error').text();
                    $('#edit-platform-error').hide();
                    $('#edit-platform-success').text("");
                    $('#edit-platform-success').hide();
        
                    $('#edit-platform-id-label').html(resp.platform_info_array.id);
                    $('#edit-platform-id').val(resp.platform_info_array.id);
                    $('#edit-platform-systemname').val(resp.platform_info_array.system_name);
                    $('#edit-platform-apikey').val(resp.platform_info_array.api_key);
                    $('#edit-platform-responsiblegroup').val(resp.platform_info_array.group_responsible_id);

                    if (resp.platform_info_array.stale_packages == true) {
                        $("#edit-platform-stalepackage").prop( "checked", true );
                    } else {
                        $("#edit-platform-stalepackage").prop( "checked", false );
                    }
                    if (resp.platform_info_array.active == true) {
                        $("#edit-platform-active").prop( "checked", true );
                    } else {
                        $("#edit-platform-active").prop( "checked", false );
                    }

                }
            }
        });      

    },
    get_platforms: function(filter_change) {
        var responsiblegroup = $('#platform-responsiblegroup-monitor').val();        
        var inactive = $('#platform-inactive-monitor').prop('checked');
        var keyword = $('#platform-keyword-monitor').val();  
              
        // $('#sensorlist-tbody').html("<tr><td colspan='5' class='text-center'>"+appmonitor.var.loader+"</td></tr>");
        $('#loading-progress').html(appmonitor_platform.var.loader);
        $.ajax({
            type: "GET",
            url: "/api/get-platform-info/",
            data: {"responsiblegroup": responsiblegroup, "inactive": inactive, "keyword": keyword},
            error: function(resp) {
                $('#platformlist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');
            },
            success: function (resp) {
                var htmlval = "";
                if (resp != null) {
                    if (resp.platform_info_array.length > 0) {
                        for (let i = 0; i < resp.platform_info_array.length; i++) {
                                var severity_color = 'btn-dark'
                                button_json = '{"id": "'+resp.platform_info_array[i].id+'"}'
                                htmlval+= "<tr>";                                                                                                      
                                htmlval+= "     <td>"+resp.platform_info_array[i].system_name+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].operating_system_name+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].operating_system_version+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].python_version+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].django_version+"</td>";
                                
                                // htmlval+= "     <td>"+resp.platform_info_array[i].vulnerability_total+"</td>";
                                if (resp.platform_info_array[i].platform_current_severity == "LOW" ) {
                                    severity_color = "btn-dark"
                                }                            
                                if (resp.platform_info_array[i].platform_current_severity == "MEDIUM" ) {
                                    severity_color = "btn-primary"
                                }                                
                                if (resp.platform_info_array[i].platform_current_severity == "HIGH" ) {
                                    severity_color = "btn-warning"
                                }  
                                if (resp.platform_info_array[i].platform_current_severity == "CRITICAL" ) {
                                    severity_color = "btn-danger"
                                }    
                                htmlval+= "     <td>";
                                
                                if (resp.platform_info_array[i].vulnerability_total > 0) {
                                    htmlval+= "     <a title='Python' type='button' class='btn "+severity_color+"' style='cursor:pointer;' href='/platform/view/"+resp.platform_info_array[i].id+"/python-packages?only_vulnerable=true'>"+resp.platform_info_array[i].vulnerability_total+"</a>";
                                } else {
                                    htmlval+= "     <a title='Python' type='button' class='btn btn-success' style='cursor: default ;'>"+resp.platform_info_array[i].vulnerability_total+"</a>";

                                }
                                if (resp.platform_info_array[i].vulnerability_total_debian > 0) {
                                    htmlval+= "     <a title='Ubuntu' type='button' class='btn "+severity_color+"' style='cursor:pointer;' href='/platform/view/"+resp.platform_info_array[i].id+"/debian-packages?only_vulnerable=true'>"+resp.platform_info_array[i].vulnerability_total_debian+"</a>";
                                } else {
                                    htmlval+= "     <a title='Ubuntu' type='button' class='btn btn-success' style='cursor: default ;'>"+resp.platform_info_array[i].vulnerability_total_debian+"</a>";

                                }     
                                if (resp.platform_info_array[i].vulnerability_total_npm > 0) {
                                    htmlval+= "     <a title='NPM/Node' type='button' class='btn "+severity_color+"' style='cursor:pointer;' href='/platform/view/"+resp.platform_info_array[i].id+"/node-packages?only_vulnerable=true'>"+resp.platform_info_array[i].vulnerability_total_npm+"</a>";
                                } else {
                                    htmlval+= "     <a title='NPM/Node' type='button' class='btn btn-success' style='cursor: default ;'>"+resp.platform_info_array[i].vulnerability_total_npm+"</a>";

                                }                                                                                             
                                
                                if (resp.platform_info_array[i].git_repo_name.length > 0) {
                                    if (resp.platform_info_array[i].dependabot_vulnerability_total > 0) {
                                        htmlval+= "     <a title='DependaBot' type='button' class='btn btn-danger' style='cursor:pointer;' href='/platform/view/"+resp.platform_info_array[i].id+"/dependabot'>"+resp.platform_info_array[i].dependabot_vulnerability_total+"</a>";
                                    } else {
                                        htmlval+= "     <a title='DependaBot' type='button' class='btn btn-success' style='cursor: default ;' href='/platform/view/"+resp.platform_info_array[i].id+"/dependabot'>"+resp.platform_info_array[i].dependabot_vulnerability_total+"</a>";

                                    }
                                } else {

                                   htmlval+= " &nbsp;";
                                }
                                htmlval+= "     </td>";

                                htmlval+= "     <td>"+resp.platform_info_array[i].group_responsible_group_name+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].last_sync_dt+"</td>"; 
                                // htmlval+= "     <td>"+resp.platform_info_array[i].updated+"</td>";                                

                                htmlval+= "     <td>";
                                if (appmonitor_platform.var.edit_platform_access == 'True') {
                                    htmlval+= "     <button class='btn btn-primary btn-sm platform-edit-btn' id='platform-edit-btn-"+resp.platform_info_array[i].id+"' data-json='"+button_json+"' >Edit</button>";
                                }
                                htmlval+= "     <a class='btn btn-primary btn-sm' href='/platform/view/"+resp.platform_info_array[i].id+"/python-packages'>View</a>";

                                htmlval+= "     </td>";
                                htmlval+= "</tr>";
                            
                        }

                        $('#platformlist-tbody').html(htmlval);
                        $(".platform-edit-btn").on( "click", function() {
                            var btndata_json = $(this).attr('data-json');
                            var btndata = JSON.parse(btndata_json);
                            appmonitor_platform.get_update_platform_by_id(btndata['id'])
                            // appmonitor_platform.edit_platform();  
                            $("#EditPlatformModal").modal("show");
                                     
                        });
                        
                    } else {
                        $('#platformlist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');                    
                    }   
                    $('#loading-progress').html(""); 
                    if (filter_change == false) {
                        setTimeout("appmonitor_platform.get_platforms()", 60000);
                    }                      
                } else {
                    $('#platformlist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');
                    $('#loading-progress').html("");
                }
                
            }
        })        
    }, 
    byteToHex: function(byte) {
        return ('0' + byte.toString(16)).slice(-2);
    },
    generateId: function(len = 100) {
        var arr = new Uint8Array(len / 2);
        window.crypto.getRandomValues(arr);
        return Array.from(arr, appmonitor_platform.byteToHex).join("");
    }
}
