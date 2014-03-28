$(document).ready(function()
{
  //Disable tabs in the navigation
  $('li.disabled > a').click(function(e) {
    e.preventDefault();
    return false;
  });

  //Make all outgoing links open in a new page
  $("a[href^='http']").attr('target','_blank');
  
  //Enable affix behavior on sidenav
  $('#sidebar').affix({
    offset: {
      top: $("#mainContent").offset().top
    }
  });
  //Enable popovers
  $('#help').popover(options)
});