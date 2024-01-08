var appmonitor_packages = {
    var: {
        loader: '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>',
    },
    init: function() {
        appmonitor_packages.get_platform_packages();
        $( "#package_search_btn" ).on( "click", function() {
            appmonitor_packages.get_platform_packages();   
        });
        $("#package_search").on('keyup', function (e) {
            if (e.key === 'Enter' || e.keyCode === 13) {
                appmonitor_packages.get_platform_packages();   
            }
        })
    },
    get_platform_packages: function() {
        data = {}
        url_params = "?"
        var package_search = $('#package_search').val();
        if (package_search.length > 0) {
            url_params += '&search_package='+package_search;
        }
        // $('#sensorlist-tbody').html("<tr><td colspan='5' class='text-center'>"+appmonitor.var.loader+"</td></tr>");
        $('#loading-progress').html(appmonitor_packages.var.loader);
        $.ajax({
            type: "GET",
            url: "/api/get-platform-packages-info/"+url_params,
            data: data,
            error: function(resp) {
                $('#platformpackageslist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');
            },
            success: function (resp) {
                var htmlval = "";
                if (resp != null) {
                    if (resp.platform_packages_info_array.length > 0) {
                        for (let i = 0; i < resp.platform_packages_info_array.length; i++) {
                          
                                htmlval+= "<tr>";                                                                                                      
                                htmlval+= "     <td><a href='/platform/view/"+resp.platform_packages_info_array[i].platform_id+"/'>"+resp.platform_packages_info_array[i].system_name+"</a></td>";
                                htmlval+= "     <td>"+resp.platform_packages_info_array[i].package_name+"</td>";
                                htmlval+= "     <td>"+resp.platform_packages_info_array[i].current_package_version+"</td>";
                                htmlval+= "     <td>"+resp.platform_packages_info_array[i].python_version+"</td>";
                                htmlval+= "     <td>"+resp.platform_packages_info_array[i].django_version+"</td>";
                                htmlval+= "     <td>"+resp.platform_packages_info_array[i].group_responsible_group_name+"</td>";
                                htmlval+= "     <td>"+resp.platform_packages_info_array[i].updated+"</td>";                                
                            
                                htmlval+= "</tr>";
                            
                        }

                        $('#platformpackageslist-tbody').html(htmlval);
                        
                    } else {
                        $('#platformpackageslist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');                    
                    }   
                    $('#loading-progress').html(""); 
                    setTimeout("appmonitor_platform.get_platforms()", 60000)                      
                } else {
                    $('#platformpackageslist-tbody').html('<tr><td colspan="8" class="text-center">No Results</td></tr>');
                    $('#loading-progress').html("");
                }
                
            }
        })        
    }
}
