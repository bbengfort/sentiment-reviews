$(document).ready(function() {
  console.info("starting sentiment reviews application");
  let fetchTimeout = undefined;

  const reviewsTemplate = _.template($("#reviewsTemplate").text());

  const polarityClass = function(polarity) {
    switch (polarity) {
      case "UNK":
        return "text-muted";
      case "NEG":
        return "text-danger";
      case "NEU":
        return "text-primary";
      case "POS":
        return "text-success";
    }
    return "text-info";
  }

  const polarityText = function(polarity) {
    switch (polarity) {
      case "UNK":
        return "unknown";
      case "NEG":
        return "negative";
      case "NEU":
        return "neutral";
      case "POS":
        return "positive";
    }
    return "bleh";
  }

  // in miliseconds
  const units = {
    year  : 24 * 60 * 60 * 1000 * 365,
    month : 24 * 60 * 60 * 1000 * 365/12,
    day   : 24 * 60 * 60 * 1000,
    hour  : 60 * 60 * 1000,
    minute: 60 * 1000,
    second: 1000
  }

  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  const getRelativeTime = (d1, d2 = new Date()) => {
    const elapsed = d1 - d2

    // "Math.abs" accounts for both "past" & "future" scenarios
    for (var u in units)
      if (Math.abs(elapsed) > units[u] || u == 'second')
        return rtf.format(Math.round(elapsed/units[u]), u)
  }

  // Load the reviews from the API
  const loadReviews = function() {
    $.get({
      url: "/api/reviews/",
      dataType: "json"
    })
    .done(function(data) {
      if (data.results) {
        data.polarityClass = polarityClass;
        data.polarityText = polarityText;
        data.getRelativeTime = getRelativeTime;

        let reviews = reviewsTemplate(data);
        $("#reviews").html($(reviews));
      }

      // Schedule the next batch of reviews to be fetched in 5 seconds
      fetchTimeout = setTimeout(loadReviews, 5000);
    }).fail(function(jqXHR, textStatus, errorThrown) {
      console.error(textStatus, errorThrown);
      if (jqXHR.responseJSON) {
        addAlert(jqXHR.responseJSON.detail);
      } else {
        addAlert(errorThrown);
      }
    });
  }

  const alertTemplate = _.template($("#alertTemplate").html());

  const addAlert = function(msg) {
    let alert = alertTemplate({msg: msg});
    $("#alerts").append($(alert));
  }

  // Load the initial batch of reviews from the server.
  loadReviews();

  // Handle form submit
  $('form').submit(function(e) {
    e.preventDefault();
    if (fetchTimeout) {
      // Stop fetching reviews while we post the new review.
      clearTimeout(fetchTimeout);
    }

    // Disable the buttons
    const form = $(this);
    $("form button").attr("disabled", true);

    const data = form
      .serializeArray()
      .reduce(function (json, {name, value}) {
        json[name] = value;
        return json;
      }, {});

    // Post the form to the server
    $.post({
      url: "/api/reviews/",
      data: data,
      dataType: "json"
    }).done(function(data) {
      $("#text").val("");
    }).fail(function(jqXHR, textStatus, errorThrown) {
      console.error(textStatus, errorThrown);
      if (jqXHR.responseJSON.detail) {
        addAlert(jqXHR.responseJSON.detail);
      } else {
        addAlert(errorThrown);
      }
    }).always(function() {
     $("form button").removeAttr("disabled");
     loadReviews();
    });

    return false
  })

  // Character counting application
  $('textarea').keyup(function() {
    var characterCount = $(this).val().length,
        current = $('#currentCount'),
        maximum = $('#maximumCount'),
        theCount = $('#charsCounter');

    current.text(characterCount);

    if (characterCount < 200) {
      current.removeClass('text-primary text-warning text-danger');
      current.addClass('text-muted');
    }
    if (characterCount > 200 && characterCount < 250) {
      current.removeClass('text-muted text-warning text-danger');
      current.addClass('text-primary');
    }
    if (characterCount > 250 && characterCount < 280) {
      current.removeClass('text-muted text-primary text-danger');
      current.addClass('text-warning');
    }
    if (characterCount > 280 && characterCount < 300) {
      current.removeClass('text-muted text-primary text-warning');
      current.addClass('text-danger');
    }

    if (characterCount >= 300) {
      current.removeClass('text-muted text-primary text-warning');
      maximum.addClass('text-danger');
      current.addClass('text-danger');
      theCount.css('font-weight','bold');
    } else {
      maximum.removeClass('text-danger');
      theCount.css('font-weight','normal');
    }
  });

});