var attached = null;
var dialog = null;
var highlight = null;

function attach_media_upload(type, id) {
	var ret = {type:type, id:id};
	attached = ret;
}

function attach_highlight_position(page_id, start_index, end_index, start_offset, end_offset) {
	var ret_highlight = {
		page_id:       page_id,
		start:         start_index,
		end:           end_index,
		start_offset:  start_offset,
		end_offset:    end_offset
	};
	highlight = ret_highlight;
}

(function($){
	// When the documet is ready
	$(function() {
		// Define the click action for publish button
		// When uers click the publish button, call the publish() function
		$('#postbox .btn-publish').click(publish);
		$('#postbox .post-btn').css({"font-size":"100%", "padding":"0px 5px", "margin-right":"3px"});
		$('#postbox .post-btn').hover(function(){
			$(this).css({"background-color":"rgb(57, 181, 136)"});
		},function(){
			$(this).css({"background-color":"gray"});
		})
		// Define the click action for image attaching button
		// When uers click the image button, call the openDialog() function
		$('.postbox .toolbar a.toolbar-btn').click(openDialog);

		// Add the highlighting functions here
		$("#viewerContainer #viewer").mouseup(function(event){
 	    	if (window.getSelection){// For standard browsers: Chrome, Firefox...
 	    		var selection = window.getSelection();
        		if (selection.rangeCount > 0) {
        			var selectionRange = selection.getRangeAt(0); //Range对象
            		var startNode = selectionRange.startContainer.parentNode;
            		var endNode = selectionRange.endContainer.parentNode;
            		if (startNode && endNode) {
            			var start_index = $(startNode).index(); // Get Start selected node
            			var end_index = $(endNode).index(); // Get Last selected node
            			if (end_index <= start_index) {
            				alert("Error happened in javascript. Please try again later.");
            				return false;
            			}
            			var start_offset = selectionRange.startOffset;
	            		var end_offset = selectionRange.endOffset;
	            		if (start_offset < 0)
	            			start_offset = 0;
	            		if (end_offset < 0)
	            			end_offset = 0;

            			// Get book page no.
            			var pageNode = $(startNode).parent().parent();
            			var page_id = $(pageNode).attr('id').replace(/[^0-9]/ig,"");
            			attach_highlight_position(page_id, start_index, end_index, start_offset, end_offset);
            		}
        		}

        		return false;
 	    	}

 			if (document.selection){// For IE: ToDo
 				selection_elements = document.selection.createRange();
 				return false;
 			}

	    	return false;
		});

		// Add the highlighting function for a selected annotation node
		// @TODO Define an ajax request type for retrieving the highlight information for an annotation
		$(".node-annotation.node-teaser").hover(function(event){
			if( $(this).hasClass('sending') ){
				alert(Drupal.t('System is processing your request. Please wait...'));
				return false;
			}

			// Get the annotationId from current selection node
			var annotationId = $(this).attr('id').split('-')[1];
			// Refer to the codes for obtaining the book page no.

			if (annotationId > 0) {
				var data = {
					act: 'getHightlight', // Add response actions for this act
					annotation_id: annotationId
				};

				var that = this;
				var option = ajaxOption();
				option = $.extend(option, {
					data : data,
					complete : function(){
						$("#node-"+annotationId).removeClass('sending');
					},
					success : function(json) {
	          if (json.error) {
              ajaxError(json.error);
	          }
	          else if (json.success){
							if ($('svg')) {
								$('svg').remove();
							};
              addHighlight(json.highlight.page_id, json.highlight.highlight_start, json.highlight.highlight_end, 0, 0);

							if (json.highlight.page_id) {
		    				var page_container = $("#pageContainer" + json.highlight.page_id + " .textLayer");
								if( page_container.length > 0) {
									var focus_node = page_container.children("div").eq(json.highlight.highlight_end);
								}
								var line = '<path d="M ' + ($(that).offset().left) + ' ' + ($(that).offset().top + 80) + ' '
																	+ 'L ' + (focus_node.offset().left) + ' ' + (focus_node.offset().top) + ' '
																	+ '" fill="transparent" stroke="black"></path>';
								var svg = '<svg version="1.1" baseProfile="full" width="' + $('html').width()
													+ '" height="' + $('html').height()
													+ '" xmlns="http://www.w3.org/2000/svg" style="pointer-events: none; position: absolute; top: 0;">'
													+ line + '</svg>';
								$(svg).appendTo($('body'));
							};
	          }
					}
				});

				$(this).addClass('sending');
				$.ajax(option);
			}

			return false;
		});
	});

	function ajaxOption(){
		return {
			url  : Drupal.settings.annotation.ajax_url,
			type : 'POST',
			dataType : 'json',
			timeout : Drupal.settings.annotation.timeout * 1000,
			error : ajaxError
		};
	}

	function ajaxError(jqXHR, textStatus, errorThrown){
		switch(textStatus){
		case 'error':
		 	$msg = 'Error happened in sending the request. Please try again later.';
		  break;
		case 'timeout':
		 	$msg = 'Request timeout. Please check your network connection or try again later.';
		 	break;
		default:
			$msg = textStatus;
		}

		alert(Drupal.t($msg));
	}

    // The openDialog() function for clicking the image button
	function openDialog(){
		if( !dialog ){
			// init the dialog
			dialog = $('<div id="postbox-dialog"></div>').hide().appendTo($('body'));

			// Define the close button for the dialog
			// Define the click event for the close button
			$('<a href="javascript:void(0);" class="btn-close"></a>')
			.appendTo(dialog)
			.click(closeDialog);
		}

		if( !dialog.is(':visible') ) {
			var content = $('#image-dialog');
			// Check the existense of the image upload dialog
			if( content.length == 0 ) {
				content = create_image_dialog();
				content.addClass('dialog');
			}
			content.show().appendTo(dialog);
			var pos = $(this).offset();
			dialog.css('left', pos.left-360).css('top', pos.top + 15).slideDown();
		}

		return false;
	}

    // The closeDialog() function for clicking the dialog close button
	function closeDialog() {
		resetDialog();
		return false;
	}

	function resetDialog(){
		if( dialog ) {
			dialog.hide();
			attached = null;
			var remove_btn = $('input#edit-fid-remove-button');
			if( remove_btn.length != 0 ){
				remove_btn.mousedown();
			}
			$('.dialog', dialog).hide().appendTo($('body'));
		}
	}

	function create_image_dialog(){
		var imageDialog = $('<div id="image-dialog"></div>');
		var upload_tab = $('#image-uploader');
		if(upload_tab.length != 0){
			upload_tab.show().css({position:'', left:''}).appendTo(imageDialog);
		}

		return imageDialog;
	}

    // The publish() function for clicking the publish button
	function publish(){
		if( $(this).hasClass('sending') ){
			alert(Drupal.t('System is processing your request. Please wait...'));
			return false;
		}

		var text = $.trim($('#postbox #rp-annotation').val());
		if(text == '') {
			alert(Drupal.t('Please add some texts in the comment box.'));
			return false;
		}
		var data = {
			act: 'publish',
			msg: text,
			book_id: Drupal.settings.annotation.annotation_bid
		};

		if( attached ) {
			data.attach = attached;
		}

		if ( highlight ) {
			data.highlight = highlight;
		}

		var option = ajaxOption();
		option = $.extend(option, {
			data : data,
			complete : function(){
				$('#postbox .btn-publish').removeClass('sending');
			},
			success : function(json) {
                if (json.error) {
                    ajaxError(json.error);
                }
                else if (json.success){
                    $("#start").val('');
                    $("#end").val('');
                    $('#postbox #rp-annotation').val('');
                    closeDialog();
                	window.location.reload();
                }
			}
		});

		$(this).addClass('sending');
		$.ajax(option);

		return false;
	}

	// The addHighlight() function for show the highlighting texts for an annotation
	function addHighlight(page_id, start_index, end_index, start_offset, end_offset) {
		if (start_index < 0 || end_index < 0)
			return;

		if(window.getSelection) {
		   if (window.getSelection().empty) {
		     window.getSelection().empty();
		   } else if (window.getSelection().removeAllRanges) {  // Firefox
		     window.getSelection().removeAllRanges();
		   }

		    // Show highlights
		    var page_container = $("#pageContainer"+page_id+" .textLayer");
		    if( page_container.length > 0) {
				var anchor_node = page_container.children("div").get(start_index);
				var focus_node = page_container.children("div").get(end_index);
				if (anchor_node && focus_node) {
					var selection_element = window.getSelection();
				    var range = document.createRange();
				    range.setStart(anchor_node, start_offset); // Set the default offset as 0
				    range.setEnd(focus_node, end_offset); // Set the default offset as 0
				    selection_element.addRange(range);
				}
			}
		} else if (document.selection) {  // IE @TODO
		  document.selection.empty();
		}

		return false;
	}

})(jQuery);
