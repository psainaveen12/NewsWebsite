<?php
if (! defined('ABSPATH')) {
	exit;
}
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo('charset'); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#content"><?php esc_html_e('Skip to content', 'ieltstask-theme'); ?></a>

<header class="site-header">
	<div class="site-header__inner">
		<a class="branding" href="<?php echo esc_url(home_url('/')); ?>">
			<span class="branding__name"><?php bloginfo('name'); ?></span>
			<span class="branding__tagline"><?php bloginfo('description'); ?></span>
		</a>

		<nav class="site-nav" aria-label="<?php esc_attr_e('Primary menu', 'ieltstask-theme'); ?>">
			<?php
			wp_nav_menu(
				[
					'theme_location' => 'primary',
					'container'      => false,
					'fallback_cb'    => false,
					'depth'          => 1,
				]
			);
			?>
		</nav>
	</div>
</header>

<main id="content" class="site-shell page-section">
