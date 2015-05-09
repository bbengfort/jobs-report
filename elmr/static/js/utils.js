/*
 * Utility functions for general use in the ELMR application
 * Created: Fri May 08 17:51:57 2015 -0400
 */

/*
 * Accepts an object and returns a GET query string (no ?)
 */
function encodeQueryData(data) {
  var ret = [];
  for (var d in data)
    ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(data[d]));
  return ret.join("&");
}

/*
 *  Year Slider Management
 *  Allows the ability to manage time via period, year series in a slider
 *  Similar to the slider bar, this implements a range and value method.
 */
function YearSlider() {

  // Properties of the period object
  this.minDate  = null;   // lower boundary of the period (moment obj)
  this.maxDate  = null;   // upper boundary of the period (moment obj)
  this.period   = null;   // the period of the data (moment-range obj)
  this.is_range = false;  // if this is a range slider or not
  this.dateFmt  = null;   // the format of the date strings
  this.current  = null;   // the current value of the slider
  this.range    = null;   // the current range of the slider
  this.callback = null;   // the callback for the on slide event


  // DOM Objects for the slider
  this.elem     = null;  // the originating element (the id of the form)
  this.form     = null;  // the form that contains the slider
  this.slider   = null;  // the slider object that starts manipulation
  this.displays = [];    // the inputs to update with the values

  /*
   *  Pass in the ID selector of the form for the year range
   *  The form should include a .year-slider div and inputs for display
   *  You can also pass in as many options as you'd like
   */
  this.init = function(elem, opts) {
    var self = this;
    var defaults = {
      minDate: "Jan 2000",
      maxDate: new Date(),
      is_range: false,
      dateFmt: "MMM YYYY",
      callback: null
    }

    var options   = _.defaults(opts || {}, defaults);
    _.extend(self, options);

    // Initialize the moment objects
    this.minDate  = moment(this.minDate);
    this.maxDate  = moment(this.maxDate);
    this.period   = moment.range(this.minDate, this.maxDate);

    // Initialize the DOM
    this.elem     = elem;
    this.form     = $(elem);
    this.slider   = this.form.find('.year-slider');
    this.displays = this.form.find('.year-display');

    // Initialize the values
    var maxValue = self.period.diff("months");
    this.current = maxValue;
    this.range = [this.current - 18, this.current];

    // Initialize the slider
    if (this.is_range) {
      this.slider.slider({
        range: true,
        min: 0,
        max: maxValue,
        values: this.range,
        slide: self.onSlide()
      });
    } else {
      this.slider.slider({
        max: maxValue,
        value: this.current,
        slide: self.onSlide()
      });
    }

    // Set the displays
    self.updateDisplayFields();

    return this;
  }


  /*
  * Gets the month number in the period of the app.
  * If the date isn't within the period, returns null.
  * Use this function for setting the slider.
  */
  this.getMonthInPeriod = function(date) {
    if (!date.within(this.period)) {
      return null;
    }

    return moment.range(this.minDate, date).diff("months");
  }

  /*
   * Returns a moment object from a month number in the period of the app.
   * Use this function for getting dates from the slider.
   */
  this.getMonthFromPeriod = function(num) {
    var date = moment(this.minDate)
    date.add(num, "months");
    return date;
  }

  /*
   *  On slide handler
   */
  this.onSlide = function() {
    var self = this;
    return function(event, ui) {
      if (self.is_range) {
        // Set range to the range of values
        self.range = ui.values;
        // Set current to the rightmost value
        self.current = ui.values[1];
      } else {
        self.current = ui.value;
      }

      self.updateDisplayFields();

      if (self.callback) {
        self.callback(event, self, ui);
      }
    }
  }

  /*
   * Sets the start and end text fields from the current values
   */
  this.updateDisplayFields = function() {
    if(this.is_range) {
      if (this.displays.length != 2) {
        throw new Error("Not enough displays!")
      }
    } else {
      var date = this.getMonthFromPeriod(this.current).format(this.dateFmt);
      this.displays.val(date);
      this.displays.data("period", this.current_date());
      this.displays.data("slider", this.current);
    }
  }

  /*
   * Helper function for getting current date string
   */
  this.current_date = function() {
    return this.getMonthFromPeriod(this.current).format(this.dateFmt);
  }

  /*
   * Helper function for getting curent range date strings
   */
  this.date_range = function() {
    return _.map(this.range, function(num) {
      return this.getMonthFromPeriod(num).format(this.dateFmt);
    });
  }

}
