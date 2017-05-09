$(function() {
		$('input[type=text][name=title]').tooltip({ /*or use any other selector, class, ID*/
			placement: "right",
			trigger: "hover"
		});
		$('textarea[name=body]').tooltip({ /*or use any other selector, class, ID*/
			placement: "right",
			trigger: "hover"
		});
		$('input[type=text][name=embed]').tooltip({ /*or use any other selector, class, ID*/
			placement: "right",
			trigger: "hover"
		});
	} );

$(document).ready(function($) {
    $('.popover-link').each(function() {
        $(this).popover({
            html: true,
            trigger: 'manual',
			content: function() {
				return $('#popoverhiddencontent').html();
			},
        }).click(function(e) {
            $(this).popover('toggle');
            $('#close').click(function(e){
                $(this).parents('.popover').remove();
            });
        });
    }); 
});
	
$(document).ready(function() {
		$('#body').summernote({
			height: 300,
			toolbar: [
				['style', ['bold', 'italic', 'underline', 'clear']],
				['color', ['color']],
				['para', ['ul', 'ol', 'paragraph']],
				['insert', ['link', 'picture','table']],
				['misc', ['codeview']],
			],
			oninit: function() {
				// Add "open" - "save" buttons
				var noteBtn = '<button id="makeSnote" type="button" class="btn btn-default btn-sm btn-small" title="Insert Styled Link" data-event="something" tabindex="-1"><i class="fa fa-plus-square"></i></button>';            
				var fileGroup = '<div class="note-file btn-group">' + noteBtn + '</div>';
				$(fileGroup).appendTo($('.note-toolbar'));
				// Button tooltips
				$('#makeSnote').tooltip({container: 'body', placement: 'bottom'});
				// Button events
				$('#makeSnote').click(function(event) {
					var highlight = window.getSelection(),  
						spn = document.createElement('a'),
						range = highlight.getRangeAt(0)
					
					spn.innerHTML = highlight;
					spn.className = 'btn btn-success';
				
					range.deleteContents();
					range.insertNode(spn);
				});

			},
		});
});