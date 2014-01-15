$(document).ready(function()
{
  //Disable tabs in the navigation
  $('li.disabled > a').click(function(e) {
    e.preventDefault();
    return false;
  });
  //Enable affix behavior on sidenav
  $('#sidebar').affix({
    offset: {
      top: function() {
        return $("#mainContent").offset().top
      },
      bottom: 75
    }
  });
});