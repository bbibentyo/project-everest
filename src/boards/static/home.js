$(function(){
    let $tempChart = $("#temperature-chart");
    $.ajax({
        url: $tempChart.data("url"),
        success: function (data) {
            new Chart($tempChart[0].getContext("2d"), {
            type: 'line',
            data: {
                // labels: data.labels,
                datasets: data.datasets
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Temperature readings'
                },
                scales: {
                    xAxes: [{
                        display: true,
                        type: 'time',
                        distribution: 'series',
                        time: {
                            displayFormats: {
                                minute: 'h:mm a'
                            }
                        }
                    }]
                }
            }
        });
        },
        error: function (request, status, err) {
            console.error(err);
            console.log("completed with status: " + status);
            console.log("error message: " + err)
        }
    });

    // request humidity data
    let $humidity = $("#humidity-chart");
    $.ajax({
        url: $humidity.data("url"),
        success: function (data) {
            new Chart($humidity[0].getContext("2d"), {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Humidity readings'
                },
                scales: {
                    xAxes: [{
                        display: true,
                        type: 'time',
                        distribution: 'series',
                        time: {
                            displayFormats: {
                                minute: 'h:mm a'
                            }
                        }
                    }]
                }
            }
        });
        },
        error: function (request, status, err) {
            console.log("completed with status: " + status);
            console.log("error message: " + err)
        }
    })
});

