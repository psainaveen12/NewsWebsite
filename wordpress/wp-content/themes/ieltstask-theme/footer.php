<?php
if (! defined('ABSPATH')) {
	exit;
}
?>
</main>

<footer class="site-footer">
	<div class="site-footer__inner">
		<nav class="site-nav" aria-label="<?php esc_attr_e('Footer menu', 'ieltstask-theme'); ?>">
			<?php
			wp_nav_menu(
				[
					'theme_location' => 'footer',
					'container'      => false,
					'fallback_cb'    => false,
					'depth'          => 1,
				]
			);
			?>
		</nav>

		<div class="trust-links">
			<a href="<?php echo esc_url(home_url('/about/')); ?>"><?php esc_html_e('About', 'ieltstask-theme'); ?></a>
			<a href="<?php echo esc_url(home_url('/contact/')); ?>"><?php esc_html_e('Contact', 'ieltstask-theme'); ?></a>
			<a href="<?php echo esc_url(home_url('/privacy-policy/')); ?>"><?php esc_html_e('Privacy Policy', 'ieltstask-theme'); ?></a>
			<a href="<?php echo esc_url(home_url('/terms/')); ?>"><?php esc_html_e('Terms', 'ieltstask-theme'); ?></a>
			<a href="<?php echo esc_url(home_url('/disclaimer/')); ?>"><?php esc_html_e('Disclaimer', 'ieltstask-theme'); ?></a>
			<a href="<?php echo esc_url(home_url('/editorial-policy/')); ?>"><?php esc_html_e('Editorial Policy', 'ieltstask-theme'); ?></a>
		</div>

		<p class="site-footer__meta">
			<?php
			printf(
				/* translators: %d: current year */
				esc_html__('Copyright %d IELTSTask. Built for migration, search visibility, and operational reliability.', 'ieltstask-theme'),
				esc_html((string) gmdate('Y'))
			);
			?>
		</p>
	</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
