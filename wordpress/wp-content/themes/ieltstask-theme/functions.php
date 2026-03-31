<?php
if (! defined('ABSPATH')) {
	exit;
}

function ieltstask_theme_setup(): void {
	add_theme_support('title-tag');
	add_theme_support('post-thumbnails');
	add_theme_support(
		'html5',
		[
			'comment-form',
			'comment-list',
			'gallery',
			'caption',
			'search-form',
			'style',
			'script',
		]
	);

	register_nav_menus(
		[
			'primary' => __('Primary Menu', 'ieltstask-theme'),
			'footer'  => __('Footer Menu', 'ieltstask-theme'),
		]
	);
}
add_action('after_setup_theme', 'ieltstask_theme_setup');

function ieltstask_enqueue_assets(): void {
	wp_enqueue_style(
		'ieltstask-fonts',
		'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap',
		[],
		null
	);

	wp_enqueue_style(
		'ieltstask-style',
		get_stylesheet_uri(),
		['ieltstask-fonts'],
		wp_get_theme()->get('Version')
	);
}
add_action('wp_enqueue_scripts', 'ieltstask_enqueue_assets');

function ieltstask_posted_on(): void {
	printf(
		'<span>%s</span><span>%s</span>',
		esc_html(get_the_date()),
		esc_html(get_the_author())
	);
}

function ieltstask_excerpt_more(string $excerpt): string {
	if (is_admin()) {
		return $excerpt;
	}

	return $excerpt . sprintf(
		' <a class="read-more" href="%s">%s</a>',
		esc_url(get_permalink()),
		esc_html__('Continue reading', 'ieltstask-theme')
	);
}
add_filter('the_excerpt', 'ieltstask_excerpt_more');
