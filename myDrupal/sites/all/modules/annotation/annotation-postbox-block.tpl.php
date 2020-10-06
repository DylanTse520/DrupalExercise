<div id="postbox" class="postbox clearfix">
	<input id="highlight" type="hidden">
	<input id="highlight_for_index" type="hidden">
	<input id="start" type="hidden">
	<input id="end" type="hidden">
	<textarea id="rp-annotation"></textarea>
	<div id= "media_bar" class="toolbar clearfix">
		<a href="#image-dialog" class="btn-photo toolbar-btn" title="<?php print t('Embed Image'); ?>"></a>
		<button class="btn-publish toolbar-btn post-btn"><?php print t('Publish'); ?></button>
	</div>
</div>
<?php if ($image_uploader): ?>
	<div id="image-uploader" style="position: absolute;left: -10000px;"><?php print $image_uploader; ?></div>
<?php endif; ?>