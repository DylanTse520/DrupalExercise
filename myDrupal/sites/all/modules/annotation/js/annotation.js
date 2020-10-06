var attached = null;
var dialog = null;

function attach_media_upload(type, id) {
	var ret = {type:type, id:id};
	attached = ret;
}

function attach(type, ret, html){
	attached = ret;

	jQuery('.ajax-status', dialog).remove();
	jQuery('.dialog', dialog).hide();
	jQuery('<div class="attached">' + html + '</div>').hide().appendTo(dialog).fadeIn();
}

(function($){
	$(function() {
		$('#postbox .btn-publish').click(publish);
		$('.postbox .toolbar a.toolbar-btn').click(openDialog);
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

	function ajaxBeforeSend(loadingMsg){
		var status = $('.ajax-status', dialog);

		if( status.length == 0 )
		status = $('<div class="ajax-status"></div>').appendTo(dialog);

		status.removeClass('ajax-error').addClass('loading').css('line-height', parseInt(status.height()) + 'px').html('<span class="loading-img"></span>' + loadingMsg);
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

		if( $('.ajax-status', dialog).length != 0 ){
			$('.ajax-status', dialog).removeClass('loading').css('line-height', '').addClass('ajax-error').html(Drupal.t($msg));
		} else {
			alert(Drupal.t($msg));
		}
	}

	function ajaxComplete(){
		if( !$('.ajax-status', dialog).hasClass('ajax-error') ) {
			$('.ajax-status', dialog).remove();
			$('input[name="src"]', dialog).val('');
		}
	}

	function openDialog(){
		if( !dialog ){
			// init the dialog
			dialog = $('<div id="postbox-dialog"></div>').hide().appendTo($('body'));

			$('<a href="javascript:void(0);" class="btn-close"></a>')
			.appendTo(dialog)
			.click(closeDialog);

			// add switch tab actions within the dialog
			$('#postbox-dialog .tabs a').live('click', function(){
				if( $(this).hasClass('active') )
				return false;

				var hide_id = $('.tabs a.active', dialog).attr('href').replace(/^.*#/, '#');
				var show_id = $(this).attr('href').replace(/^.*#/, '#');

				$('.tabs a.active', dialog).removeClass('active');
				$(this).addClass('active');

				$(hide_id, dialog).hide();
				$(show_id, dialog).show();

				$('.ajax-status', dialog).remove();
				$('input[name="url"]', dialog).val('');

				return false;
			});

			// bind enter key to the input in the dialog
			$('#postbox-dialog .dialog input[name="url"]').live('keyup', function(e){
				if( e.which==13 ){
					$(this).next('.btn-attach').trigger('click');
				}
			});
		}

		var show = false;
		var id = $(this).attr('href').replace(/^.*#/, '#');
		if( dialog.is(':visible') ){
			var active_id = '#' + $('.dialog', dialog).attr('id');
			if( active_id != id ){
				if( closeDialog() ){
					show = true;
				}
			}
		} else {
			show = true;
		}

		if( show ){
			var content = $(id);
			if( content.length == 0 ) {
				var fn = 'create_' + id.replace('#', '').replace('-', '_');
				content = eval(fn + '()');
				content.addClass('dialog');
			}
			content.show().appendTo(dialog);
			var pos = $(this).offset();
			dialog.css('left', pos.left-360).css('top', pos.top + 15).slideDown();
		}

		return false;
	}

	function closeDialog() {
		resetDialog();
		return false;
	}

	function resetDialog(){
		if( dialog ) {
			dialog.hide();

			attached = null;
			$('.attached', dialog).remove();

			var remove_btn = $('input#edit-fid-remove-button');
			if( remove_btn.length != 0 ){
				remove_btn.mousedown();
			}

			$('.ajax-status', dialog).remove();
			$('input[name="url"]', dialog).val('');
			$('.dialog', dialog).hide().appendTo($('body'));
		}
	}

	function create_image_dialog(){
		var imageDialog = $('<div id="image-dialog"></div>');
		var tabs = $('<div class="tabs"><li><a href="#url-tab" class="active">' + Drupal.t('Add from URL') + '</a></li></div>');
		var url_tab = $('<div class="tab" id="url-tab"><label>' + Drupal.t('URL: ') + '</label><input type="text" required value="" name="url"><input type="submit" value="' + Drupal.t('Add') + '" class="btn-attach form-submit"></div>');
		imageDialog.append(tabs).append(url_tab);
		var upload_tab = $('#image-uploader');
		if(upload_tab.length != 0){
			tabs.append('<li><a href="#image-uploader">' + Drupal.t('Upload image') + '</a></li>');
			upload_tab.hide().css({position:'', left:''}).addClass('tab').appendTo(imageDialog);
		}

		$('.btn-attach', imageDialog).click(function(){
			var url = $('input[name="url"]', imageDialog).val();
			if( url == '' )
			return false;

			var image = new Image();
			ajaxBeforeSend(Drupal.t('Loading image, please wait...') );
			image.onerror = function(){
				ajaxError(null, 'Error loading the image. Please check if the image url is correct.');
			};
			image.onload  = function(){
				attach('image', {type:'image', url:url}, '<img src="' + url + '">');
			};
			image.src = url;
		});

		return imageDialog;
	}

	function publish(){
		if( dialog && $('.loading', dialog).length != 0 ) {
			alert( $('.loading', dialog).text() );
			return false;
		}

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
			book_id: Drupal.settings.annotation.annotation_bid,
			start: $.trim($("#postbox #start").val()),
			end: $.trim($("#postbox #end").val())
		};

		if( attached ){
			data.attach = attached;
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

})(jQuery);
