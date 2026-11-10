import {defineConfig, loadEnv} from 'vite';
import vue from '@vitejs/plugin-vue';
import {fileURLToPath, URL} from 'node:url';

export default defineConfig(({mode}) => {
    const env = loadEnv(mode, '.', '');

    return {
        base: env.VITE_BASE ?? '/',
        plugins: [vue()],
        resolve: {
            alias: {'@': fileURLToPath(new URL('./src', import.meta.url))},
        },
        css: {
            preprocessorOptions: {
                scss: {
                    api: 'modern',
                    additionalData: '@import "@/assets/styles/shared-resources.scss";\n',
                    silenceDeprecations: ['import'],
                },
            },
        },
        server: {
            host: true,
            port: Number(env.VITE_PORT ?? 5173),
            proxy: {
                '/api': {
                    target: env.VITE_DEV_API_TARGET ?? 'http://localhost:8000',
                    changeOrigin: true,
                },
            },
        },
    };
});
