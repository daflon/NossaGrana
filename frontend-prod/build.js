const fs = require('fs-extra');
const path = require('path');
const { minify } = require('html-minifier');
const CleanCSS = require('clean-css');
const UglifyJS = require('uglify-js');

const sourceDir = path.join(__dirname, 'public');
const buildDir = path.join(__dirname, 'build');

console.log('🚀 Iniciando build de produção...');

// Limpar diretório de build
if (fs.existsSync(buildDir)) {
    fs.removeSync(buildDir);
}
fs.ensureDirSync(buildDir);

// Configurações de minificação
const htmlMinifyOptions = {
    removeComments: true,
    removeRedundantAttributes: true,
    removeScriptTypeAttributes: true,
    removeStyleLinkTypeAttributes: true,
    sortClassName: true,
    useShortDoctype: true,
    collapseWhitespace: true,
    minifyCSS: true,
    minifyJS: true
};

const cssMinifier = new CleanCSS({
    level: 2,
    returnPromise: false
});

// Função para processar arquivos HTML
function processHTML(filePath, outputPath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const minified = minify(content, htmlMinifyOptions);
    fs.writeFileSync(outputPath, minified);
    console.log(`✅ HTML: ${path.basename(filePath)}`);
}

// Função para processar arquivos CSS
function processCSS(filePath, outputPath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const result = cssMinifier.minify(content);
    fs.writeFileSync(outputPath, result.styles);
    console.log(`✅ CSS: ${path.basename(filePath)}`);
}

// Função para processar arquivos JS
function processJS(filePath, outputPath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const result = UglifyJS.minify(content, {
        compress: {
            drop_console: true,
            drop_debugger: true
        },
        mangle: true
    });
    
    if (result.error) {
        console.warn(`⚠️  Erro ao minificar ${path.basename(filePath)}: ${result.error}`);
        fs.copyFileSync(filePath, outputPath);
    } else {
        fs.writeFileSync(outputPath, result.code);
    }
    console.log(`✅ JS: ${path.basename(filePath)}`);
}

// Processar todos os arquivos
function processDirectory(srcDir, destDir) {
    const items = fs.readdirSync(srcDir);
    
    items.forEach(item => {
        const srcPath = path.join(srcDir, item);
        const destPath = path.join(destDir, item);
        
        if (fs.statSync(srcPath).isDirectory()) {
            fs.ensureDirSync(destPath);
            processDirectory(srcPath, destPath);
        } else {
            const ext = path.extname(item).toLowerCase();
            
            switch (ext) {
                case '.html':
                    processHTML(srcPath, destPath);
                    break;
                case '.css':
                    processCSS(srcPath, destPath);
                    break;
                case '.js':
                    processJS(srcPath, destPath);
                    break;
                default:
                    fs.copyFileSync(srcPath, destPath);
                    console.log(`📄 Copiado: ${item}`);
            }
        }
    });
}

// Executar build
try {
    processDirectory(sourceDir, buildDir);
    
    // Criar arquivo de configuração para produção
    const config = {
        buildTime: new Date().toISOString(),
        version: require('./package.json').version,
        environment: 'production'
    };
    
    fs.writeFileSync(
        path.join(buildDir, 'build-info.json'),
        JSON.stringify(config, null, 2)
    );
    
    console.log('\n🎉 Build concluído com sucesso!');
    console.log(`📁 Arquivos gerados em: ${buildDir}`);
    
    // Estatísticas
    const stats = getDirectoryStats(buildDir);
    console.log(`📊 Total de arquivos: ${stats.files}`);
    console.log(`📦 Tamanho total: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
    
} catch (error) {
    console.error('❌ Erro durante o build:', error);
    process.exit(1);
}

function getDirectoryStats(dir) {
    let files = 0;
    let size = 0;
    
    function scan(directory) {
        const items = fs.readdirSync(directory);
        items.forEach(item => {
            const itemPath = path.join(directory, item);
            const stat = fs.statSync(itemPath);
            
            if (stat.isDirectory()) {
                scan(itemPath);
            } else {
                files++;
                size += stat.size;
            }
        });
    }
    
    scan(dir);
    return { files, size };
}