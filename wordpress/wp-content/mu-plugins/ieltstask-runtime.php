<?php
/**
 * Plugin Name: IELTSTask Runtime Helpers
 * Description: Production runtime helpers for the self-hosted EC2 deployment.
 */

if (! defined('ABSPATH')) {
	exit;
}

add_filter('xmlrpc_enabled', '__return_false');
add_filter('the_generator', '__return_empty_string');
remove_action('wp_head', 'wp_generator');

add_action(
	'rest_api_init',
	static function (): void {
		register_rest_route(
			'ieltstask/v1',
			'/health',
			[
				'methods'             => 'GET',
				'permission_callback' => '__return_true',
				'callback'            => static function (): WP_REST_Response {
					global $wpdb;

					$db_ok = false;

					if ($wpdb instanceof wpdb) {
						$db_ok = (bool) $wpdb->get_var('SELECT 1');
					}

					return new WP_REST_Response(
						[
							'status'      => $db_ok ? 'ok' : 'degraded',
							'site'        => home_url('/'),
							'environment' => wp_get_environment_type(),
							'database'    => $db_ok ? 'ok' : 'error',
						],
						$db_ok ? 200 : 503
					);
				},
			]
		);
	}
);
