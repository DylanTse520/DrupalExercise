<div id="postbox" class="postbox clearfix">
	<textarea id="rp-annotation"></textarea>
	<div id= "media_bar" class="toolbar clearfix">
		<a href="#image-dialog" class="btn-photo toolbar-btn" title="<?php print t('Upload Image'); ?>"></a>
		<button class="btn-publish toolbar-btn post-btn"><?php print t('Publish'); ?></button>
	</div>
</div>
<?php if ($image_uploader): ?>
	<div id="image-uploader" style="position: absolute;left: -10000px;"><?php print $image_uploader; ?></div>
<?php endif; ?>