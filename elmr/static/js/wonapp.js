/*
 * Implements the code for handling a multi-timeseries graph
 */
function WealthOfNations() {

  // DOM Elements
  this.elem = null;
  this.svg  = null;
  this.selector = null;

  // Other properties
  this.margin = {top: 9.5, right: 23.5, bottom: 24.5, left: 39.5};
  this.nations = null;
  this.dateFmt = "MMM YYYY";
  this.minDate = moment("Jan 2000", this.dateFmt);
  this.maxDate = moment("Feb 2015", this.dateFmt);
  this.period  = moment.range(this.minDate, this.maxDate);
  this.months  = this.period.diff("months")

  // A bisector since many nations' data is sparse
  this.bisect = d3.bisector(function(d) {
    return moment(d[0], "MMM YYYY");
  });

  // Graph properties
  // Various scales that are make assumptions of the data domain.
  this.xScale = d3.scale.log().domain([261991, 18944974]);
  this.yScale = d3.scale.linear().domain([1.7, 15.4]);
  this.radiusScale = d3.scale.sqrt().domain([248642, 17668292]).range([0,40]);
  this.colorScale  = d3.scale.category10();

  // X and Y Axes
  this.xAxis  = d3.svg.axis().orient("bottom").ticks(12, d3.format(",d"));
  this.gXaxis = null;
  this.yAxis  = d3.svg.axis().orient("left");
  this.gYaxis = null
  this.label  = null;
  this.gDot   = null;

  // Pass in a selector to initialize the view
  this.init = function(selector) {
    var self = this;
    this.selector = selector;
    this.elem = $(selector);

    // Init the X and Y Scales and the axes
    this.xScale.range([0, this.width(true)]);
    this.yScale.range([this.height(true), 0]);
    this.xAxis.scale(this.xScale);
    this.yAxis.scale(this.yScale);

    // Init the SVG element inside of the chart
    this.svg = d3.select(selector).append("svg")
        .attr("width", this.width())
        .attr("height", this.height())
      .append("g")
        .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");

    // Add the X-Axis
    this.gXaxis = this.svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + this.height(true) + ")")
      .call(this.xAxis);

    // Add the Y-Axis
    this.gYaxis = this.svg.append("g")
      .attr("class", "y axis")
      .call(this.yAxis);

    // Add an x-axis label.
    this.svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "end")
        .attr("x", this.width(true))
        .attr("y", this.height(true) - 6)
        .text("income per capita, inflation-adjusted (dollars)");

    // Add a y-axis label.
    this.svg.append("text")
        .attr("class", "y label")
        .attr("text-anchor", "end")
        .attr("y", 6)
        .attr("dy", ".75em")
        .attr("transform", "rotate(-90)")
        .text("life expectancy (years)");

    // Add the year label; the value is set on transition.
    this.label = this.svg.append("text")
        .attr("class", "year label")
        .attr("text-anchor", "end")
        .attr("y", this.height(true) - 24)
        .attr("x", this.width(true))
        .text("Jan 2000");

    return self;
  }

  // Accessors that specify the four dimension of data to visualize
  // These need to be corrected for our data types on demand.
  this.x = function(d) { return d.income; }
  this.y = function(d) { return d.lifeExpectancy; }
  this.radius = function(d) { return d.population; }
  this.color  = function(d) { return d.region; }
  this.key    = function(d) { return d.name; }

  // Load the data
  this.fetch_data = function(callback) {
    var self = this;
    // var url  = "/api/regions/"
    var url = "/static/data/regions.json";
    d3.json(url, function(nations) {
      self.nations = nations;

      // Add a dot per nation, intialize and set colors.
      self.gDot = self.svg.append("g")
          .attr("class", "dots")
        .selectAll(".dot")
          .data(self.interpolateData(0))
        .enter().append("circle")
          .attr("class", "dot")
          .style("fill", function(d) { return self.colorScale(self.color(d)); })
          .call(function(d) { self.position(d) })
          .sort(function(a,b) { self.order(a,b) });

      // Add a title.
      self.gDot.append("title")
        .text(function(d) { return d.name; });

      // Add an overlay for the year label.
      var box = self.label.node().getBBox();
      var overlay = self.svg.append("rect")
        .attr("class", "overlay")
        .attr("x", box.x)
        .attr("y", box.y)
        .attr("width", box.width)
        .attr("height", box.height)
        .on("mouseover", function() { self.enableInteraction(box, overlay) });

      // Start a transition that interpolates the data based on year.
      self.svg.transition()
        .duration(30000)
        .ease("linear")
        .tween("year", function() { self.tweenYear() })
        .each("end", self.enableInteraction);

      if (callback) {
        callback();
      }

    });
  }

  // Position dots based on data
  this.position = function(dot) {
    var self = this;
    dot.attr("cx", function(d) { return self.xScale(self.x(d)); })
      .attr("cy", function(d) { return self.yScale(self.y(d)); })
      .attr("r", function(d) { return self.radiusScale(self.radius(d)); });
  }

  // Defines a sort order so small dots are drawn on top
  this.order = function(a, b) {
    return this.radius(b) - this.radius(a);
  }

  // After transition finishes, mousover to change the year.
  this.enableInteraction = function(box, overlay) {
    var self = this;
    var yearScale = d3.scale.linear()
      .domain([0, self.months])
      .range([box.x + 10, box.x + box.width - 10])
      .clamp(true);

    // Cancle the current transition, if any.
    this.svg.transition().duration(0);

    overlay
      .on("mouseover", mouseover)
      .on("mouseout", mouseout)
      .on("mousemove", mousemove)
      .on("touchmove", mousemove);

    function mouseover() {
      self.label.classed("active", true);
    }

    function mouseout() {
      self.label.classed("active", false);
    }

    function mousemove() {
      self.displayYear(yearScale.invert(d3.mouse(this)[0]));
    }

  }

  // Tweens the entire chart by first tweeing the year, and then the data.
  // For the interpolated data, the dots and label are redrawn.
  this.tweenYear = function() {
    var self = this;
    var year = d3.interpolateNumber(0,self.months);
    return function(t) { self.displayYear(year(t)); };
  }

  // Updates the display to show the specified year.
  this.displayYear = function(year) {
    var self = this;
    self.gDot.data(self.interpolateData(year), self.key)
      .call(function(d) { self.position(d) })
      .sort(function(a,b) { self.order(a,b) });



    var date = moment(self.minDate)
    date.add(year, "months");

    self.label.text(date.format(self.dateFmt));
  }

  // Interpolates the dataset for the given (fractional) year.
  this.interpolateData = function(year) {
    var self = this;
    return this.nations.map(function(d) {
      return {
        name: d.name,
        region: d.region,
        income: self.interpolateValues(d.income, year),
        population: self.interpolateValues(d.population, year),
        lifeExpectancy: self.interpolateValues(d.lifeExpectancy, year)
      };
    });
  }

  // Finds (and possibly interpolates) the value for the specified year.
  this.interpolateValues = function(values, months) {
    var date = moment(this.minDate)
    date.add(months, "months");

    var i = this.bisect.left(values, date, 0, values.length - 1),
        a = values[i];

    return a[1];
  }

  // Helper function to parse a date string (uses moment not d3)
  this.parse_date = function(dtstr) {
    return moment(dtstr, this.dateFmt);
  }

  // Helper functions to get the width from the element
  // If the inner argument is true, the margins are subtracted
  this.width = function(inner) {
    if (inner) {
      return this.elem.width() - this.margin.right - this.margin.left;
    } else {
      return this.elem.width();
    }

  }

  // Helper functions to get the height from the element
  // If the inner argument is true, the margins are subtracted
  this.height = function(inner) {
    if (inner) {
      return this.elem.height() - this.margin.top - this.margin.bottom;
    } else {
      return this.elem.height();
    }

  }

}


$(function() {

  /*************************************************************************
  ** Initialization
  *************************************************************************/

  var chart = new WealthOfNations().init("#wealthofnationsChart");
  chart.fetch_data(function() {
    console.log("Wealth of Nations Application Started");
  });


});
