import path from 'path'
import adapter from '@sveltejs/adapter-static'
import { enhancedImages } from '@sveltejs/enhanced-img'
import { sveltekit } from '@sveltejs/kit/vite'
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'
import { config as dotEnvConfig } from 'dotenv'
import Icons from 'unplugin-icons/vite'
import { defineConfig } from 'vite'

// have to configure dotenv to load correct .env file
dotEnvConfig({ path: `.env.${process.env.NODE_ENV}` })

// only proxy API in development; in production it is proxied by Caddy
const proxyAPI = !!process.env.VITE_PROXY_API

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
	resolve: {
		alias: {
			$constants: path.resolve(import.meta.dirname, '../constants')
		}
	},
	server: {
		proxy: proxyAPI
			? {
					// proxy API endpoint to FastAPI
					'/api': {
						target: 'http://localhost:5000',
						changeOrigin: true
					}
				}
			: undefined
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
			}
		}),
		Icons({ compiler: 'svelte' })
	]
})
