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
		$('#postbox #publishannotation.btn-publish').click(publish);

		// Define the click action for image attaching button
		// When uers click the image button, call the openDialog() function
		$('.postbox .toolbar a.toolbar-btn').click(openDialog);

		// Define the click action for enrich button
		// When uers click the enrich button, call the enrich() function
		$('#postbox #autoenrich.btn-enrich').click(function(event){
			$('#block-annotation-annotation-block').toggle();
			$('#block-annotation-enrichment-block').toggle();
		});

		$('#postbox .post-btn').css({"font-size":"100%", "padding":"0px 5px", "margin-right":"3px"});
		$('#postbox .post-btn').hover(function(){
			$(this).css({"background-color":"rgb(57, 181, 136)"});
		},function(){
			$(this).css({"background-color":"gray"});
		})
		$('body').click(function(){
			$('svg').remove()
		})
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
            			if (end_index < start_index) {
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
		$("#block-annotation-annotation-block .node-annotation.node-teaser").hover(function(event){
			showHighlight("annotation", this);
		});
		$("#block-annotation-enrichment-block .node-annotation.node-teaser").hover(function(event){
			showHighlight("enrichment", this);
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

	function showHighlight(type, that){

		if( $(that).hasClass('sending') ){
			alert(Drupal.t('System is processing your request. Please wait...'));
			return false;
		}

		// Get the annotationId from current selection node
		var annotationId = $(that).attr('id').split('-')[1];
		// Refer to the codes for obtaining the book page no.
		if (annotationId > 0) {
			var data = {
				act: 'getHightlight', // Add response actions for this act
				annotation_id: annotationId,
				type: type
			};

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
          	var highlight_info = json.highlight;
          	// Add codes here to highlight texts
          	if (type == 'annotation') {
							if ($('svg')) {
								$('svg').remove();
							};
            	addHighlight(highlight_info.page_id, highlight_info.highlight_start, highlight_info.highlight_end, 0, 0, that);
          	}
          	else if (type == 'enrichment') {
          		if ($('svg')) {
								$('svg').remove();
							};
          		addHighlightKeyword(highlight_info.page_id, highlight_info.highlight_keywords, that);
          	}
          }
				}
			});

			$(this).addClass('sending');
			$.ajax(option);
		}

		return false;
	}

	// The function for show the highlighting texts for an annotation
	function addHighlight(page_id, start_index, end_index, start_offset, end_offset, that) {
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

				var index_node = page_container.children("div").eq(end_index);
				var line = '<path d="M ' + ($(that).offset().left) + ' ' + ($(that).offset().top + 80) + ' '
													+ 'L ' + (index_node.offset().left - 5) + ' ' + ($(that).offset().top + 80) + ' '
													+ 'L ' + (index_node.offset().left - 5) + ' ' + (index_node.offset().top) + ' '
													+ '" fill="transparent" stroke="rgba(119, 118, 254, 0.5)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round""></path>';
				var svg = '<svg version="1.1" baseProfile="full" width="' + $('#page-wrapper').width()
									+ '" height="' + $('#page-wrapper').height()
									+ '" xmlns="http://www.w3.org/2000/svg" style="pointer-events: none; position: absolute; top: 0;">'
									+ line + '</svg>';
				$(svg).appendTo($('body'));

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

	// The function for show the highlighting keywords
	function addHighlightKeyword(page_id, keyword, that) {
		if (keyword == null)
			return;
		if(window.getSelection) {
			if (window.getSelection().empty) {
				window.getSelection().empty();
			} else if (window.getSelection().removeAllRanges) {  // Firefox
				window.getSelection().removeAllRanges();
			}

	    // Show highlights
	    var page_container = $("#pageContainer" + page_id + " .textLayer");
	    if( page_container.length > 0) {
	    	words = page_container.children("div");
	    	for (var i = words.length - 1; i >= 0; i--) {
	    		if(words[i].innerText.toLowerCase().indexOf(keyword.toLowerCase().replace(new RegExp(" ","gm"),'')) != -1) {
		    		var anchor_node = page_container.children("div").get(i);
						var focus_node = page_container.children("div").get(i + 1);
		    		var index_node = page_container.children("div").eq(i);

	    			var line = '<path d="M ' + ($(that).offset().left) + ' ' + ($(that).offset().top + 80) + ' '
															+ 'L ' + (index_node.offset().left) + ' ' + ($(that).offset().top + 80) + ' '
															+ 'L ' + (index_node.offset().left) + ' ' + (index_node.offset().top) + ' '
															+ '" fill="transparent" stroke="rgba(119, 118, 254, 0.5)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round""></path>';
						var svg = '<svg version="1.1" baseProfile="full" width="' + $('#page-wrapper').width()
											+ '" height="' + $('#page-wrapper').height()
											+ '" xmlns="http://www.w3.org/2000/svg" style="pointer-events: none; position: absolute; top: 0;">'
											+ line + '</svg>';
						$(svg).appendTo($('body'));

						if (anchor_node && focus_node) {
							var selection_element = window.getSelection();
					    var range = document.createRange();
					    range.setStart(anchor_node, 0); // Set the default offset as 0
					    range.setEnd(focus_node, 0); // Set the default offset as 0
					    selection_element.addRange(range);
						}
						break;
		    	}
	    	};
			}
		} else if (document.selection) {  // IE @TODO
		  document.selection.empty();
		}
		return false;
	}

})(jQuery);
