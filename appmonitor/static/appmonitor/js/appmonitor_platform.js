var appmonitor_platform = {
    var: {
        loader: '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>',
    },
    init: function() {
        appmonitor_platform.get_platforms();

    },
    get_platforms: function() {
        
        // $('#sensorlist-tbody').html("<tr><td colspan='5' class='text-center'>"+appmonitor.var.loader+"</td></tr>");
        $('#loading-progress').html(appmonitor_platform.var.loader);
        $.ajax({
            type: "GET",
            url: "/api/get-platform-info/",
            data: {},
            error: function(resp) {
                $('#platformlist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');
            },
            success: function (resp) {
                var htmlval = "";
                if (resp != null) {
                    if (resp.platform_info_array.length > 0) {
                        for (let i = 0; i < resp.platform_info_array.length; i++) {
                          
                                htmlval+= "<tr>";                                                                                                      
                                htmlval+= "     <td>"+resp.platform_info_array[i].system_name+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].operating_system_name+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].operating_system_version+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].python_version+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].django_version+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].group_responsible_group_name+"</td>";
                                htmlval+= "     <td>"+resp.platform_info_array[i].last_sync_dt+"</td>"; 
                                htmlval+= "     <td>"+resp.platform_info_array[i].updated+"</td>";                                
                                
                                htmlval+= "     <td><a class='btn btn-primary btn-sm' href='/platform/view/"+resp.platform_info_array[i].id+"/'>View</a></td>";
                                htmlval+= "</tr>";
                            
                        }


                      

                        $('#platformlist-tbody').html(htmlval);
                        
                    } else {
                        $('#platformlist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');                    
                    }   
                    $('#loading-progress').html(""); 
                    setTimeout("appmonitor_platform.get_platforms()", 60000)                      
                } else {
                    $('#platformlist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');
                    $('#loading-progress').html("");
                }
                
            }
        })        
    }
}
