var run_button = document.getElementById("run-button");

function create_chart () {
    info = JSON.parse(this.response);
    
    window.chart_data = [];
    for (var x=0; x < info.length; x++) {
        window.chart_data.push(0)
    };

    window.chart_progress = 0

    try {
        window.graph.destroy();
    } catch (err) {}

    renderChart(window.chart_data, info.labels);
    window.chart_labels = info.labels;

    refresh_returns();
};

run_button.onclick = function() {

    var form_data = new FormData(document.getElementById("run-options"));
    var request = new XMLHttpRequest();
    request.addEventListener("load", create_chart);
    request.open("POST", '/backtest/start', true);
    request.setRequestHeader('Content-Type', 'application/json');

    form_json = Object.fromEntries(form_data);
    form_json['code'] = window.editor.getValue();
    request.send(JSON.stringify(form_json));

};

/*
function write_logs () {
    log_list = document.getElementById("log-list")
    info = JSON.parse(this.response)
    for (var x in info) {
        child = document.createElement('li')
        child.innerHTML = info[x]
        log_list.appendChild(child)
    };
};
*/

function refresh_logs () {
    var log_request = new XMLHttpRequest();
    log_request.addEventListener("load", function () {
        var log_list = document.getElementById("log-list")
        var info = JSON.parse(this.response)
        for (var x in info) {
            let child = document.createElement('li')
            child.innerHTML = info[x]
            log_list.appendChild(child)
        };
    });
    log_request.open("GET", "/logs", true);
    log_request.send();

    setTimeout(refresh_logs, 1000);
}

function update_chart () {
    info = JSON.parse(this.response);

    try {
        for (var x in info) {
            window.graph.data.datasets[0].data[window.chart_progress] = (info[x] - 1);
            window.chart_progress += 1;
            window.graph.update();
        };
        
    }
    catch (err) {}
    
}

function refresh_returns () {
    var returns_request = new XMLHttpRequest();
    returns_request.addEventListener("load", update_chart);
    returns_request.open("GET", "/returns", true);
    returns_request.send();

    setTimeout(refresh_returns, 250);
};

function renderChart(data, labels) {
    
    var ctx = document.getElementById("graph-canvas").getContext('2d');
    window.graph = new Chart(ctx, {
        type: 'LineWithLine',
        data: {
            labels: labels,
            datasets: [{
                lineTension: 0,
                label: 'Strategy',
                data: data,
                backgroundColor: 'rgba(107, 192, 232, 0.5)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            tooltips: {
                intersect: false
            },
            scales: {
                yAxes: [{
                    type: 'linear',
                    ticks: {
                        //min: 0,
                        precision: 0
                    }
                }],
                xAxes: [{
                    ticks: {
                        maxTicksLimit: 8
                    }
                }]
            },
            animation: {
                duration: 0
            },
            elements: {
                point: {
                    radius: 0
                }
            }
        }
    });
}

window.addEventListener("beforeunload", function(event) {
    var request = new XMLHttpRequest();
    request.open("POST", '/backtest/savecode', true);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify({'saved_code': window.editor.getValue()}));
})

window.onload = function() {

    window.editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
        mode: "python",
        styleActiveLine: true,
        lineNumbers: true,
        lineWrapping: true,
    });
    //window.editor.setValue("def setup(self):\n\n    self.symbol='AAPL'\
    //\n\ndef get_signals(self, event): \n\n    pass")
    window.editor.setValue(saved_code)

    this.refresh_logs();

    Chart.defaults.LineWithLine = Chart.defaults.line;
    Chart.controllers.LineWithLine = Chart.controllers.line.extend({
    draw: function(ease) {
        Chart.controllers.line.prototype.draw.call(this, ease);

        if (this.chart.tooltip._active && this.chart.tooltip._active.length) {
            var activePoint = this.chart.tooltip._active[0],
                ctx = this.chart.ctx,
                x = activePoint.tooltipPosition().x,
                topY = this.chart.scales['y-axis-0'].top,
                bottomY = this.chart.scales['y-axis-0'].bottom;

            // draw line
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(x, topY);
            ctx.lineTo(x, bottomY);
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#07C';
            ctx.stroke();
            ctx.restore();
        }
    }
    });
};