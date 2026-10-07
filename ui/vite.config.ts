import adapter from '@sveltejs/adapter-static'
import { sveltekit } from '@sveltejs/kit/vite'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'
import { defineConfig } from 'vite'
import { enhancedImages } from '@sveltejs/enhanced-img'
import Icons from 'unplugin-icons/vite'
import tailwindcss from '@tailwindcss/vite'
import { config as dotEnvConfig } from 'dotenv'

// have to configure dotenv to load correct .env file
dotEnvConfig({ path: `.env.${process.env.NODE_ENV}` })

export default defineConfig({
	build: {
		rollupOptions: {
			output: {
				// split mapbox & deck.gl into their own chunk; they are huge
				manualChunks: function (id) {
					if (id.includes('mapbox-gl') || id.includes('deck.gl')) {
						return 'map-vendor'
					}
				}
			}
		}
	},
	plugins: [
		tailwindcss(),
		enhancedImages(),
		sveltekit({
			preprocess: vitePreprocess(),

			adapter: adapter({
				pages: 'public',
				assets: 'public',
				fallback: '404.html',
				precompress: false,
				strict: true
			}),
			paths: {
				base: process.env.DEPLOY_PATH || ''
			},
			alias: {
				$constants: '../constants',
				$images: 'src/images',
				// TODO: migrate to #lib: https://svelte.dev/docs/kit/migrating-to-sveltekit-3
				$lib: 'src/lib'
			}
		}),
		Icons({ compiler: 'svelte' })
	]
})
