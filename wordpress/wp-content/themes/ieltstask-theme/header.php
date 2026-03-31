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
	<div class="site-topbar">
		<div class="site-topbar__inner">
			<nav class="site-topbar__nav" aria-label="<?php esc_attr_e('Top bar menu', 'ieltstask-theme'); ?>">
				<?php
				if (has_nav_menu('topbar')) {
					wp_nav_menu(
						[
							'theme_location' => 'topbar',
							'container'      => false,
							'menu_class'     => 'menu',
							'fallback_cb'    => false,
							'depth'          => 1,
						]
					);
				} else {
					ieltstask_render_fallback_menu('topbar', 'menu');
				}
				?>
			</nav>

			<p class="site-topbar__message"><?php esc_html_e('Independent IELTS prep content with clear editorial and advertising disclosures.', 'ieltstask-theme'); ?></p>

			<?php if (has_nav_menu('social')) : ?>
				<nav class="site-topbar__social" aria-label="<?php esc_attr_e('Social links', 'ieltstask-theme'); ?>">
					<?php
					wp_nav_menu(
						[
							'theme_location' => 'social',
							'container'      => false,
							'menu_class'     => 'menu',
							'fallback_cb'    => false,
							'depth'          => 1,
						]
					);
					?>
				</nav>
			<?php endif; ?>
		</div>
	</div>

	<div class="site-header__inner">
		<div class="site-brand">
			<?php if (has_custom_logo()) : ?>
				<div class="branding__logo"><?php the_custom_logo(); ?></div>
			<?php endif; ?>

			<a class="branding" href="<?php echo esc_url(home_url('/')); ?>">
				<span class="branding__name"><?php bloginfo('name'); ?></span>
				<span class="branding__tagline"><?php bloginfo('description'); ?></span>
			</a>
		</div>

		<nav class="site-nav" aria-label="<?php esc_attr_e('Primary menu', 'ieltstask-theme'); ?>">
			<?php
			if (has_nav_menu('primary')) {
				wp_nav_menu(
					[
						'theme_location' => 'primary',
						'container'      => false,
						'menu_class'     => 'menu',
						'fallback_cb'    => false,
						'depth'          => 1,
					]
				);
			} else {
				ieltstask_render_fallback_menu('primary', 'menu');
			}
			?>
		</nav>

		<div class="site-header__search">
			<?php get_search_form(); ?>
		</div>
	</div>
</header>

<main id="content" class="site-shell page-section">
