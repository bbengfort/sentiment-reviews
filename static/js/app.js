$(document).ready(function() {
  console.info("starting sentiment reviews application");

  // Handle form submit
  $('form').submit(function(e) {
    e.preventDefault();
    const data = $(this)
      .serializeArray()
      .reduce(function (json, {name, value}) {
        json[name] = value;
        return json;
      }, {});

    console.log(data)
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