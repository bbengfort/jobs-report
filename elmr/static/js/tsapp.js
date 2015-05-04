$(function() {

  /*************************************************************************
  ** Initialization
  *************************************************************************/

  var endpoint  = "http://127.0.0.1:5000/api/series/LAUST280000000000005/";
  var element   = $("#upper-series-view");
  var dateFmt = "MMM YYYY";

  var margin = {top: 20, right: 80, bottom: 30, left: 60},
      width = element.width() - margin.left - margin.right,
      height = 500 - margin.top - margin.bottom;

  var x = d3.time.scale()
    .range([0, width]);

  var y = d3.scale.linear()
    .range([height, 0]);

  var color = d3.scale.category10();

  var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

  var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

  var line = d3.svg.line()
    .interpolate("basis")
    .x(function(d) { return x(d.period); })
    .y(function(d) { return y(d.value); });

  var svg = d3.select("#upper-series-view").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");;

  d3.json(endpoint, function(error, data) {
    data.data.forEach(function(d) {
      d.period = moment(d.period, dateFmt);
    });


    x.domain(d3.extent(data.data, function(d) { return d.period; }));
    y.domain(d3.extent(data.data, function(d) { return d.value; }));

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Value");

    svg.append("path")
        .datum(data.data)
        .attr("class", "line")
        .attr("d", line);
  });

  var zoom = d3.behavior.zoom()
    .x(x)
    .y(y)
    .scaleExtent([1, 10])
    .on("zoom", zoomed);
	


  console.log("Time Series Application Started");

});
