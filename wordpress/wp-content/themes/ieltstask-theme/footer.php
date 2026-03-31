<?php
if (! defined('ABSPATH')) {
	exit;
}
?>
</main>

<footer class="site-footer">
	<div class="site-footer__trust">
		<div class="site-footer__trust-inner">
			<p class="site-footer__trust-text"><?php esc_html_e('Independent editorial content. Sponsored placements and advertisements are clearly identified. For corrections or business inquiries, use the Contact Us page.', 'ieltstask-theme'); ?></p>
		</div>
	</div>

	<div class="site-footer__inner">
		<section class="footer-panel">
			<p class="footer-panel__eyebrow"><?php esc_html_e('About IELTSTask', 'ieltstask-theme'); ?></p>
			<h2 class="footer-panel__title"><?php esc_html_e('A cleaner WordPress version of the existing Blogger publication.', 'ieltstask-theme'); ?></h2>
			<p><?php esc_html_e('This starter theme mirrors the Blogger XML structure with a legal topbar, sticky header, content-plus-sidebar layout, and strong footer trust messaging so migration work stays aligned with the live brand.', 'ieltstask-theme'); ?></p>
			<?php if (has_nav_menu('social')) : ?>
				<nav class="site-footer__social" aria-label="<?php esc_attr_e('Footer social links', 'ieltstask-theme'); ?>">
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
		</section>

		<section class="footer-panel">
			<p class="footer-panel__eyebrow"><?php esc_html_e('Legal Pages', 'ieltstask-theme'); ?></p>
			<ul class="footer-links">
				<?php foreach (ieltstask_get_legal_links() as $link) : ?>
					<li><a href="<?php echo esc_url($link['url']); ?>"><?php echo esc_html($link['label']); ?></a></li>
				<?php endforeach; ?>
			</ul>
		</section>

		<section class="footer-panel">
			<p class="footer-panel__eyebrow"><?php esc_html_e('Footer Navigation', 'ieltstask-theme'); ?></p>
			<nav class="site-footer__nav" aria-label="<?php esc_attr_e('Footer menu', 'ieltstask-theme'); ?>">
				<?php
				if (has_nav_menu('footer')) {
					wp_nav_menu(
						[
							'theme_location' => 'footer',
							'container'      => false,
							'menu_class'     => 'menu',
							'fallback_cb'    => false,
							'depth'          => 1,
						]
					);
				} else {
					ieltstask_render_fallback_menu('footer', 'menu');
				}
				?>
			</nav>

			<p class="site-footer__meta">
				<?php
				printf(
					/* translators: %d: current year */
					esc_html__('Copyright %d IELTSTask. Built for migration, search visibility, and operational reliability.', 'ieltstask-theme'),
					esc_html((string) gmdate('Y'))
				);
				?>
			</p>
		</section>
	</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
