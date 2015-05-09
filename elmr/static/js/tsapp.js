/*
 * Implements the code for handling a multi-timeseries graph
 */
function SeriesView() {

  // DOM Elements
  this.elem = null;
  this.svg  = null;
  this.selector = null;
  this.slider   = null;

  // The series needs to be a list of objects
  // Where each item has a period key defining the Month Year
  // And every subsequent key is the value for a particular time series
  this.series = [];

  // Defines the data fetch period and the number of elements in the series
  this.start_year  = 2000;
  this.end_year    = 2015;
  this.date_format = "MMM YYYY";

  // Base endpoint for the timeseries API
  this.base_url    = '/api/series/';

  // Other properties
  this.margin = {top: 20, right: 80, bottom: 30, left: 60};

  // Graph properties
  this.x = null;
  this.y = null;
  this.xAxis  = null;
  this.gXaxis = null;
  this.yAxis  = null;
  this.gYaxis = null;
  this.line   = null;
  this.path   = null;
  this.color  = d3.scale.category10();

  // Pass in a selector to initialize the view
  this.init = function(selector) {
    var self = this;
    this.selector = selector;
    this.elem = $(selector);

    this.svg = d3.select(this.selector).append("svg")
        .attr("width", this.width())
        .attr("height", this.height())
      .append("g")
        .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")");;

    this.x = d3.time.scale()
      .range([0, this.width(true)]);

    this.y = d3.scale.linear()
      .range([this.height(true), 0]);

    this.xAxis = d3.svg.axis()
      .scale(this.x)
      .orient("bottom");

    this.yAxis = d3.svg.axis()
      .scale(this.y)
      .orient("left");

    this.line = d3.svg.line()
      .interpolate("basis")
      .x(function(d) { return self.x(d.period); })
      .y(function(d) { return self.y(d.value); });

    return this;
  }

  // Given a BLSID, fetch the data and draw the series
  this.fetch_series = function(blsid) {
    var self = this;
    var endpoint = this.base_url + blsid;
    endpoint += "?start_year=" + this.start_year + "&end_year=" + this.end_year;

    d3.json(endpoint, function(error, response) {
      // The JSON response contains some external info like source, title, etc.
      // The series information is in a property called `data`, which contains
      // objects that have period and value properties to add to the main series.
      var data = response.data;

      data.forEach(function(d) {
        d.period = self.parse_date(d.period); // parse the date
      });

      // Temporary - we'll have to add the series to the view next.
      self.series = data;
      self.draw();

    });

  }

  // Draw the time series into the element
  this.draw = function() {

    this.x.domain(d3.extent(this.series, function(d) { return d.period; }));
    this.y.domain(d3.extent(this.series, function(d) { return d.value; }));

    if (this.gXaxis === null) {
      this.gXaxis = this.svg.append("g");
    }

    this.gXaxis
      .attr("class", "x axis")
      .attr("transform", "translate(0," + this.height(true) + ")")
      .call(this.xAxis);

    if (this.gYaxis === null) {
      this.gYaxis = this.svg.append("g");
    }

    this.gYaxis
        .attr("class", "y axis")
        .call(this.yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Value");

    if (this.path === null) {
      this.path = this.svg.append("path");
    }
    this.path
        .datum(this.series)
        .attr("class", "line")
        .attr("d", this.line);

  }


  // Helper function to parse a date string (uses moment not d3)
  this.parse_date = function(dtstr) {
    return moment(dtstr, this.date_format);
  }

  // Helper functions to get the width from the element
  // If the inner argument is true, the margins are subtracted
  this.width = function(inner) {
    if (inner) {
      return this.elem.width() - this.margin.left - this.margin.right;
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

  // Default Upper Series
  var DEFAULT_UPPER_SERIES = "LNS12300000";
  var DEFAULT_LOWER_SERIES = "LNS13000000";

  // Append "upper" and "lower" to get specific controls
  var ctrlIDs = {
    "view": "SeriesView",
    "select": "TSSelectControl",
    "label": "TSName",
    "source": "TSSource"
  }

  function initControls(prefix) {
    // Create the controls via the prefix and the selector
    var controls = _.mapObject(ctrlIDs, function(selector, key) {
      selector = "#" + prefix + selector;
      if (key=="view") {
        return new SeriesView().init(selector);
      } else {
        return $(selector);
      }
    });

    controls.fetch_series = function(blsid) {
      return this.view.fetch_series(blsid);
    }

    // Bind the selection change event
    controls.select.change(function(e) {
      var pick   = $(this).find(":selected"),
          blsid  = pick.val(),
          title  = pick.text(),
          source = pick.parent().attr("label");

      console.log(source, blsid, "selected:", title);

      controls.label.text(title);
      controls.source.text(source);
      controls.fetch_series(blsid);

    });

    return controls;
  }

  var upperControls = initControls("upper");
  var lowerControls = initControls("lower");

  upperControls.select.val(DEFAULT_UPPER_SERIES).trigger("change");
  lowerControls.select.val(DEFAULT_LOWER_SERIES).trigger("change");


  /*
   * Initialize Headlines Application
   */
  var dataUrl = "/api/source/cps/";
  var data    = null;    // holder for the CPS data
  var slider  = null;
  var dateFmt = "MMM YYYY";

  // Fetch CPS Analysis data for headlines
  $.get(dataUrl)
    .success(function(d) {
      data = d;

      console.log("Fetched data from " + dataUrl);
      console.log("Analysis period: " + data.period.start + " to " + data.period.end);

      slider = new YearSlider().init("#formTSExplorerPeriodRange", {
        is_range: true,
        minDate: moment(d.period.start, dateFmt),
        maxDate: moment(d.period.end, dateFmt),
        dateFmt: dateFmt,
        slide: function(event, slider, ui) {
          // Update the headlines with the deltas
          updateHeadlines();
        },
        change: function(event, slider, ui) {
          // Update the time series with the new range
          console.log("not implemented yet");
        }
      });

    console.log("Time Series Application Started");
  });

  /*
   * Computes headline information and updates fields.
   */
  function updateHeadlines() {
    var dp = $(".year-display");
    var sd = data.data[$(dp[0]).data("slider")];
    var ed = data.data[$(dp[1]).data("slider")];

    console.log(data);

    // Handle unemployment (left headline)
    var lh = $("#left-headline");
    lh.find(".headline-number").text(ed.LNS14000000 + "%");

    var unempDiff = (ed.LNS14000000 - sd.LNS14000000).toFixed(3);
    var p = lh.find(".headline-delta");
    if (unempDiff > 0) {
      p.html($('<i class="fa fa-long-arrow-up"></i>'))
      p.removeClass("text-success").addClass("text-danger");
    } else {
      p.html($('<i class="fa fa-long-arrow-down"></i>'))
      p.removeClass("text-danger").addClass("text-success");
    }
    p.append("&nbsp;" + Math.abs(unempDiff) + "%");

    // Handle # nonfarm jobs (right headline)
    var rh = $("#right-headline");
    rh.find(".headline-number").text(Math.round(ed.LNS12000000 / 1000) + "K");

    var jobsDiff = ed.LNS12000000 - sd.LNS12000000;
    p = rh.find(".headline-delta");
    if (jobsDiff > 0) {
      p.html($('<i class="fa fa-long-arrow-up"></i>'))
      p.removeClass("text-danger").addClass("text-success");
    } else {
      p.html($('<i class="fa fa-long-arrow-down"></i>'))
      p.removeClass("text-success").addClass("text-danger");
    }
    p.append("&nbsp;" + Math.abs(jobsDiff));
  }

});
