$(function() {

  /*************************************************************************
  ** Initialization
  *************************************************************************/

  // Important Variables
  var dateFmt = "MMM YYYY";
  var dataUrl = "/api/source/cps/";
  var data    = null;    // holder for the CPS data

  var map       = null;  // The D3 Chloropeth map object
  var minDate   = null;  // lower boundary of the period (moment obj)
  var maxDate   = null;  // upper boundary of the period (moment obj)
  var period    = null;  // the period of data (moment-range obj)
  var startDate = null;  // the start of the current range in the slider
  var endDate   = null;  // the end of the current range in the slider

  $.get(dataUrl)
    .success(function(d) {
      data = d;

      console.log("Fetched data from " + dataUrl);
      console.log("Analysis period: " + data.period.start + " to " + data.period.end);

      // Initialize the analytical period from the data
      minDate = moment(data.period.start, dateFmt);
      maxDate = moment(data.period.end, dateFmt);
      period  = moment.range(minDate, maxDate);

      startDate = moment(maxDate);       // clone date
      startDate.subtract(18, "months");  // subtract 18ddd months

      endDate = moment(maxDate);         // clone date

      // Initialize the Start and End Date inputs
      updateDateFields();

      // Initialize Year Range Slider
      $("#year-range-slider").slider({
        range: true,
        min: 0,                     // min is the zeroth value of the period
        max: period.diff("months"), // max is the number of months in the period
        values: [getMonthInPeriod(startDate), getMonthInPeriod(endDate)],
        slide: function(event, ui) {
          startDate = getMonthFromPeriod(ui.values[0]);
          endDate = getMonthFromPeriod(ui.values[1]);
          updateDateFields();
        }
      });

      var topo = "/static/data/topojson/countries/USA.json";
      var geodata = "/api/geo/laus/unemployment-rate/";


      // Initialize the Map
      map = d3.geomap.choropleth()
        .geofile(topo)
        .colors(colorbrewer.YlOrRd[9]) // See http://bl.ocks.org/mbostock/5577023 for colors
        .projection(d3.geo.albersUsa)
        .column(endDate.format(dateFmt))
        .unitId('fips')
        .scale(1000)
        .legend(true)
        .translate([455, 250]);

      // Bind window resize to the draw map function
      $(window).resize(function(e) {
        drawMap();
      });

      console.log("Fetching data for chloropeth map ...");
      // Load the CSV data for the map
      d3.csv(geodata, function(error, data) {
          d3.select('#map')
              .datum(data);

          // Turn off the loader and indicate application started
          toggleLoading(false, function() {
            drawMap(); // Draw the map
            console.log("Geography Application Started");
          });
      });

    });

  /*************************************************************************
  ** Helper Functions
  *************************************************************************/

  /*
   * Redraw the chlorpeth map on demand.
   */
  function drawMap() {
    // Set the width of the map equal to the width of the container
    var width = $("#map").width();
    map.width(width);

    // Empty the map div of the old map
    $("#map").empty();

    // Draw the map inside the map div
    d3.select('#map')
      .call(map.draw, map);
  }

  /*
   * Select handler for getting new data for the map.
   */
  $("#menuDataset li a").click(function(e) {
    e.preventDefault();
    var a = $(e.target);
    var href = a.attr('href');
    var name = a.text();
    var source = a.data().source;

    $("#menuDataset").dropdown("toggle");

    $("#datasetSource").html("Loading &hellip;");
    $("#datasetName").html("Loading &hellip;");

    d3.csv(href, function(error, data) {
        d3.select('#map').datum(data);
        drawMap();

        $("#datasetSource").text(source);
        $("#datasetName").text(name);
    });

    return false;
  });

  /*
  * Gets the month number in the period of the app.
  * If the date isn't within the period, returns null.
  * Use this function for setting the slider.
  */
  function getMonthInPeriod(date) {
    if (!date.within(period)) {
      return null;
    }

    return moment.range(minDate, date).diff("months");
  }

  /*
   * Returns a moment object from a month number in the period of the app.
   * Use this function for getting dates from the slider.
   */
  function getMonthFromPeriod(num) {
    var date = moment(minDate)
    date.add(num, "months");
    return date;
  }

  /*
   * Sets the start and end text fields from the start and end dates.
   */
  function updateDateFields() {
    $("#startDate").val(startDate.format(dateFmt));
    $("#endDate").val(endDate.format(dateFmt));

    // Update the headlines based on the date fields
    updateHeadlines();

    // Update the map to the current year
    if (map) {
      map.column(endDate.format(dateFmt));
      drawMap();
    }
  }

  /*
   * Computes headline information and updates fields.
   */
  function updateHeadlines() {
    var sd = data.data[getMonthInPeriod(startDate)];
    var ed = data.data[getMonthInPeriod(endDate)];

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

  /*
   * Toggles the loader if data needs to be reloaded for some reason.
   * Pass isLoading (true or false) to toggle loading on or off, and
   * a function for when the toggle is complete to be called after.
   */
  function toggleLoading(isLoading, complete) {
    // Set the effects here
    var appEffect = "fade";
    var ldrEffect = "drop";

    // Reset Bootstrap Hidden with jQuery Hide
    $(".hidden").hide().removeClass("hidden");
    $(".show").show().removeClass("show");

    if (isLoading) {

      // show loader gif and hide content
      $("#geographyApplication").hide(appEffect, 1000, function() {
          $("#loading").show(ldrEffect, 200, complete);
        });

    } else {

      // hide the loader gif and show content
      $("#loading").hide(ldrEffect, 1000, function() {
          $("#geographyApplication").show(appEffect, 200, complete);
        });

    }
  }

});
