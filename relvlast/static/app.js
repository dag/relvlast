$(function(){
  var creole = new Parse.Simple.Creole();

  var previewCreole = function(){
    var preview = $('#preview-' + this.id);
    preview.html('');
    creole.parse(preview.get()[0], this.value);
  }

  $('textarea.creole').each(previewCreole).keyup(previewCreole);
});
