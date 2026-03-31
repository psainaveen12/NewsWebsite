<?php
if (! defined('ABSPATH')) {
	exit;
}

function ieltstask_theme_setup(): void {
	add_theme_support('title-tag');
	add_theme_support('post-thumbnails');
	add_theme_support(
		'custom-logo',
		[
			'height'      => 80,
			'width'       => 240,
			'flex-height' => true,
			'flex-width'  => true,
		]
	);
	add_theme_support(
		'html5',
		[
			'comment-form',
			'comment-list',
			'gallery',
			'caption',
			'navigation-widgets',
			'search-form',
			'style',
			'script',
		]
	);

	register_nav_menus(
		[
			'topbar'  => __('Top Bar Menu', 'ieltstask-theme'),
			'primary' => __('Primary Menu', 'ieltstask-theme'),
			'footer'  => __('Footer Menu', 'ieltstask-theme'),
			'social'  => __('Social Links Menu', 'ieltstask-theme'),
		]
	);
}
add_action('after_setup_theme', 'ieltstask_theme_setup');

function ieltstask_register_sidebars(): void {
	register_sidebar(
		[
			'name'          => __('Primary Sidebar', 'ieltstask-theme'),
			'id'            => 'primary-sidebar',
			'description'   => __('Widgets shown beside posts, pages, and archives.', 'ieltstask-theme'),
			'before_widget' => '<section id="%1$s" class="sidebar-card widget %2$s">',
			'after_widget'  => '</section>',
			'before_title'  => '<h2 class="sidebar-card__title widget-title">',
			'after_title'   => '</h2>',
		]
	);
}
add_action('widgets_init', 'ieltstask_register_sidebars');

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

function ieltstask_get_legal_links(): array {
	return [
		[
			'label' => __('About Us', 'ieltstask-theme'),
			'url'   => home_url('/about-us/'),
		],
		[
			'label' => __('Contact Us', 'ieltstask-theme'),
			'url'   => home_url('/contact-us/'),
		],
		[
			'label' => __('Privacy Policy', 'ieltstask-theme'),
			'url'   => home_url('/privacy-policy/'),
		],
		[
			'label' => __('Terms and Conditions', 'ieltstask-theme'),
			'url'   => home_url('/terms-and-conditions/'),
		],
		[
			'label' => __('Disclaimer', 'ieltstask-theme'),
			'url'   => home_url('/disclaimer/'),
		],
		[
			'label' => __('Editorial Policy', 'ieltstask-theme'),
			'url'   => home_url('/editorial-policy/'),
		],
	];
}

function ieltstask_render_fallback_menu(string $location, string $menu_class = 'menu'): void {
	$items = [];

	switch ($location) {
		case 'primary':
			$items = [
				[
					'label' => __('Home', 'ieltstask-theme'),
					'url'   => home_url('/'),
				],
				[
					'label' => __('About Us', 'ieltstask-theme'),
					'url'   => home_url('/about-us/'),
				],
				[
					'label' => __('Editorial Policy', 'ieltstask-theme'),
					'url'   => home_url('/editorial-policy/'),
				],
				[
					'label' => __('Contact Us', 'ieltstask-theme'),
					'url'   => home_url('/contact-us/'),
				],
			];
			break;
		case 'topbar':
		case 'footer':
			$items = ieltstask_get_legal_links();
			break;
	}

	if (empty($items)) {
		return;
	}

	echo '<ul class="' . esc_attr($menu_class) . '">';

	foreach ($items as $item) {
		printf(
			'<li><a href="%1$s">%2$s</a></li>',
			esc_url($item['url']),
			esc_html($item['label'])
		);
	}

	echo '</ul>';
}

function ieltstask_posted_on(): void {
	printf(
		'<span>%s</span><span>%s</span>',
		esc_html(get_the_date()),
		esc_html(get_the_author())
	);
}

function ieltstask_breadcrumbs(): void {
	if (is_front_page()) {
		return;
	}

	echo '<nav class="breadcrumbs" aria-label="' . esc_attr__('Breadcrumb', 'ieltstask-theme') . '">';
	echo '<a href="' . esc_url(home_url('/')) . '">' . esc_html__('Home', 'ieltstask-theme') . '</a>';

	if (is_single()) {
		$categories = get_the_category();

		if (! empty($categories)) {
			echo '<span class="breadcrumbs__sep">/</span>';
			echo '<a href="' . esc_url(get_category_link($categories[0])) . '">' . esc_html($categories[0]->name) . '</a>';
		}

		echo '<span class="breadcrumbs__sep">/</span>';
		echo '<span>' . esc_html(get_the_title()) . '</span>';
	} elseif (is_page()) {
		echo '<span class="breadcrumbs__sep">/</span>';
		echo '<span>' . esc_html(get_the_title()) . '</span>';
	} elseif (is_archive()) {
		echo '<span class="breadcrumbs__sep">/</span>';
		echo '<span>' . esc_html(get_the_archive_title()) . '</span>';
	} elseif (is_search()) {
		echo '<span class="breadcrumbs__sep">/</span>';
		echo '<span>' . esc_html(sprintf(__('Search: %s', 'ieltstask-theme'), get_search_query())) . '</span>';
	}

	echo '</nav>';
}

function ieltstask_get_share_links(int $post_id = 0): array {
	$post_id = $post_id ?: get_the_ID();
	$url     = rawurlencode(get_permalink($post_id));
	$title   = rawurlencode(wp_strip_all_tags(get_the_title($post_id)));

	return [
		[
			'label' => __('Facebook', 'ieltstask-theme'),
			'url'   => 'https://www.facebook.com/sharer.php?u=' . $url,
		],
		[
			'label' => __('Twitter', 'ieltstask-theme'),
			'url'   => 'https://twitter.com/intent/tweet?url=' . $url . '&text=' . $title,
		],
		[
			'label' => __('LinkedIn', 'ieltstask-theme'),
			'url'   => 'https://www.linkedin.com/shareArticle?mini=true&url=' . $url . '&title=' . $title,
		],
		[
			'label' => __('WhatsApp', 'ieltstask-theme'),
			'url'   => 'https://api.whatsapp.com/send?text=' . $title . '%20' . $url,
		],
		[
			'label' => __('Email', 'ieltstask-theme'),
			'url'   => 'mailto:?subject=' . $title . '&body=' . $url,
		],
	];
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
