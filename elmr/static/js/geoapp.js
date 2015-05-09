$(function() {

  /*************************************************************************
  ** Initialization
  *************************************************************************/

  // Important Variables
  var map       = null;  // The D3 Chloropeth map object
  var geoSlider = new YearSlider().init("#formGeographyPeriodRange", {
    minDate: "Jan 2000",
    maxDate: "Feb 2015",
    change: function(event, slider, ui) {
      // Update the map to the current year
      if (map) {
        map.column(slider.current_date());
        drawMap();
      }
    }
  });

  // Important endpoints
  var topo = "/static/data/topojson/countries/USA.json";
  // var geodata = "/api/geo/laus/unemployment-rate/";
  var geodata = "/static/data/unemployment-rate.csv";


  // Initialize the Map
  map = d3.geomap.choropleth()
    .geofile(topo)
    .colors(get_color_scale())
    .projection(d3.geo.albersUsa)
    .column(geoSlider.current_date())
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
    map.colors(get_color_scale());

    // Empty the map div of the old map
    $("#map").empty();

    // Draw the map inside the map div
    d3.select('#map')
      .call(map.draw, map);
  }

  /*
   * Determines what color scale to use based on the dataset.
   * See http://bl.ocks.org/mbostock/5577023 for colors
   *
   */
  function get_color_scale() {

    var s = 9;

    colors = {
      PuBu: colorbrewer.PuBu[s],
      RdPu: colorbrewer.RdPu[s],
      RdYlGn: colorbrewer.RdYlGn[s],
      YlOrRd: colorbrewer.YlOrRd[s],
      PiYG: colorbrewer.PiYG[s],
      YlGnBu: colorbrewer.YlGnBu[s]
    }

    var c = $('input[name=colorRadios]:checked', '#formGeographyDataset').val();
    return colors[c];
  }

  /*
   * Handler for color scale change (to prevent entire dataset reload)
   */
   $('input:radio[name=colorRadios]', '#formGeographyDataset').change(function(e) {
     if ($(this).is(':checked')) {
       drawMap();
     }
   });

  /*
   * Select handler for getting new data for the map.
   */
  $("#formGeographyDataset").submit(function(e) {
    e.preventDefault();

    var pick   = $("#menuGeographyDataset").find(":selected"),
        href   = pick.val(),
        name   = pick.text(),
        source = pick.data().source;

    var chk_adjust = $("#chkGeoIsAdjust").is(":checked");
    var chk_delta  = $("#chkGeoIsDelta").is(":checked");

    href += "?is_adjusted=" + chk_adjust + "&is_delta=" + chk_delta;
    console.log("Fetching geographic data from", href);

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
