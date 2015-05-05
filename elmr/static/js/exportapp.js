$(function() {

  /*************************************************************************
  ** Initialization
  *************************************************************************/

  var geoEndpoint = "/api/geo/";

  // Populate the dataset selector for the Choropleth download
  $.get(geoEndpoint, function(data) {
    var selectData  = $("#cdfDataset");

    if (data.sources.length != 2) {
      console.log("Error: Expected only the LAUS and CESSM datasets! Something has changed!!!");
    }

    $.when(
      $.get(data.sources[1].url),
      $.get(data.sources[0].url)
    ).done(function(r1, r2) {

      _.each([r1, r2], function(result) {
        result = result[0];
        var optgroup = $("<optgroup></optgroup>").attr("label", result.title);

        _.each(result.datasets, function(obj) {
          optgroup.append($("<option></option>").attr("value", obj.url).text(obj.name));
        });

        selectData.append(optgroup);
      });

      $("#cfdDatasetPlaceholder").text("Select dataset to download");
      selectData.removeAttr("disabled");

      console.log("Data Export Application Started")


    });

  });

  // Bind the download submit to the action
  $("#choroplethDownloadForm").submit(function(e) {
    e.preventDefault();

    var endpoint = $("#cdfDataset option:selected").val();

    if (!endpoint) {
      return
    }

    var delta = $("#cfdNormalize").is(":checked");
    var start = $("#cdfStartYear").val();
    var end   = $("#cdfEndYear").val();

    if (delta) {
      console.log("Normalized data set not implemented yet!");
    }

    if (start && end) {
      endpoint += "?start_year=" + start + "&end_year=" + end;
    } else if (start) {
      endpoint += "?start_year=" + start
    } else if (end) {
      endpoint += "?end_year=" + end;
    }

    console.log("Downloading dataset from", endpoint);
    window.location.href = endpoint;

    return false;
  });

});
