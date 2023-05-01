var appmonitor = {
    var: {
        loader: '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>',
    },
    init: function() {
        appmonitor.get_checks();
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
                        for (let i = 0; i < resp.monitors.length; i++) {
                            htmlval+= "<tr>";                                                                         
                            htmlval+= "     <td>";                            
                            if (resp.monitors[i].status == 0 ) {
                                htmlval+= "<div class='bg-secondary status-box-white' style='font-size: 10px; padding-top: 7px;'>UNKNOWN</div>";
                            } else if (resp.monitors[i].status == 1 ) {
                                htmlval+= "<div class='bg-danger status-box-white' >DOWN</div>";
                            } else if (resp.monitors[i].status == 2 ) {
                                htmlval+= "<div class='bg-warning status-box-white' >WARN</div>";
                            } else if (resp.monitors[i].status == 3 ) {
                                htmlval+= "<div class='bg-success status-box-white' >UP</div>";
                            }
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
                            htmlval+= "     <td><a class='btn btn-primary btn-sm' href='/monitor/history/"+resp.monitors[i].id+"/'>History</a></td>";
                            htmlval+= "</tr>";

                        }
                        $('#sensorlist-tbody').html(htmlval);

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
