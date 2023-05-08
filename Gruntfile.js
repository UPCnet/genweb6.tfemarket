module.exports = function (grunt) {
    'use strict';

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        compass: {
            css: {
                options: {
                    sassDir: 'scss/',
                    cssDir: 'stylesheets/',
                }
            }
        },
        concat: {
            options: {
                separator: '',
            },
            css: {
                src: ['stylesheets/theme.css'],
                dest: 'stylesheets/theme-concat.css',
            }
        },
        cssmin: {
            css : {
                src : ["stylesheets/theme-concat.css"],
                dest : "stylesheets/theme-tfemarket.min.css",
            }
        },
        watch: {
            css: {
                files: [
                    'scss/*'
                ],
                tasks: ['compass:css', 'concat:css', 'cssmin:css']
            },
        },
        uglify: {
            js: {
                files: {
                    'js/market.min.js': '../content/market/market.js',
                    'js/widget-codirector.min.js': '../widgets/codirector/codirector.js',
                    'js/widget-modality.min.js': '../widgets/modality/modality.js',
                    'js/widget-student.min.js': '../widgets/student/student.js',
                    'js/widget-teacher.min.js': '../widgets/teacher/teacher.js',
                    'js/widget-teacher-if-teacher.min.js': '../widgets/teacher/teacher-if-teacher.js',
                    'js/tfemarket_utils_offer.min.js': '../browser/views_templates/tfemarket_utils_offer.js',
                    'js/tfemarket_utils_rename_offer.min.js': '../browser/views_templates/tfemarket_utils_rename_offer.js',
                    'js/tfemarket_utils_stats.min.js': '../browser/views_templates/tfemarket_utils_stats.js'
                }
            }
        },
        browserSync: {
            plone: {
                bsFiles: {
                    src : [
                      'stylesheets/*.css'
                    ]
                },
                options: {
                    watchTask: true,
                    debugInfo: true,
                    proxy: "localhost:8080/Plone",
                    reloadDelay: 3000,
                    // reloadDebounce: 2000,
                    online: true
                }
            }
        }
    });

    // grunt.loadTasks('tasks');
    grunt.loadNpmTasks('grunt-browser-sync');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    // CWD to theme folder
    grunt.file.setBase('./src/genweb6/tfemarket/theme');

    // Registered tasks: grunt watch
    grunt.registerTask('default', ["browserSync:plone", "watch"]);
    grunt.registerTask('bsync', ["browserSync:html", "watch"]);
    grunt.registerTask('plone-bsync', ["browserSync:plone", "watch"]);
    grunt.registerTask('minify', ["uglify:js"]);
};
