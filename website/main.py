from nicegui import native, ui
from scripts import search

@ui.page("/")
@ui.page('/{_:path}')
def layout():
    ui.add_head_html('''
        <style>
            body {
                background-color: #f5f0ff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .purple-gradient {
                background: linear-gradient(135deg, #6a0dad 0%, #9b4dca 100%);
            }
            .result-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(106, 13, 173, 0.2) !important;
            }
            .search-container {
                position: relative;
                z-index: 10;
            }
            .search-bar {
                border-radius: 5px !important;
                background: linear-gradient(90deg, #f3e5ff 0%, #e1cfff 100%);
                padding: 10px;
                color: #ff0000;
            }
            .search-bar input {
                background-color: transparent !important;
            }
            .search-button {
                margin: 0 4px;
            }
            .logo-text {
                line-height: 1.2;
            }
        </style>
    ''')
    zandberg = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Adrian_Zandberg_Sejm_2020.jpg/800px-Adrian_Zandberg_Sejm_2020.jpg"
    with ui.column().classes('w-full h-screen fixed -z-10 flex items-center justify-center'):
        ui.image(zandberg).classes('w-[70%] h-[100%] object-cover opacity-20')
    
    with ui.right_drawer(fixed=False, value=False).classes('bg-white p-4') as options_panel:
        ui.label('Search Options').classes('text-xl font-bold text-purple-800 mb-4')
        
        idf_checkbox = ui.checkbox('Enable IDF (Inverse Document Frequency)').classes('mb-2 text-purple-800').props("color='purple'")
        
        ui.label('Search Type:').classes('mt-2 text-purple-800')
        search_type = ui.select(['Basic', 'Normalized', 'Noise Reduced'], value='Basic').classes('w-full mb-4 text-purple-800').props("color='purple'")
        
        k_column = ui.column()
        ui.label('Noise Reduction (k-value):').bind_visibility_from(search_type, 'value', backward=lambda v: v == 'Noise Reduced').classes('mt-2 text-purple-800')
        k_slider = ui.slider(min=1, max=2000, value=100).bind_visibility_from(search_type, 'value', backward=lambda v: v == 'Noise Reduced').classes('w-full text-purple-800').props("color='purple'")
        ui.label().bind_text_from(k_slider, 'value', lambda v: f'Current: {v}').bind_visibility_from(search_type, 'value', backward=lambda v: v == 'Noise Reduced').classes('text-purple-600 text-sm')
        
        ui.label('Number of entries to show:').classes('mt-4 text-purple-800')
        results_slider = ui.slider(min=1, max=20, value=10).classes('w-full text-purple-800').props("color='purple'")
        ui.label().bind_text_from(results_slider, 'value', lambda v: f'Current: {v}').classes('text-purple-600 text-sm')
        
    with ui.column().classes('w-full max-w-4xl hidden mx-auto mt-4') as results_section:
        ui.label('Top Results').classes('text-2xl font-bold text-purple-900 mb-4')
        with ui.column().classes('w-full gap-4') as results_container:
            pass
    
    def show_results():
        use_idf = idf_checkbox.value
        search_type_value = search_type.value
        k_value = k_slider.value if search_type_value == 'Noise Reduced' else None
        results_count = results_slider.value
        
        search_type_mapping = {
            'Basic': 'dumb',
            'Normalized': 'dumbvec',
            'Noise Reduced': 'smart'
        }
        
        query = search_input.value
        
        if not query:
            ui.notify("Please enter a search query", type='warning')
            return
        

        print(f"Searching with IDF: {use_idf}, Search Type: {search_type_value}, k-value: {k_value}, Results Count: {results_count}")
        results = search(
            query=query,
            idf=use_idf,
            searchtype=search_type_mapping.get(search_type_value, 'dumb'),
            samplek=k_value if k_value is not None else 3,
            howmanyresults=results_count
        )
            
        results_section.set_visibility(True)
        results_section.clear()
            
        for result in results:
            with ui.card().classes('w-full result-card transition-all shadow-md hover:shadow-xl border-l-4 border-purple-500'):
                with ui.column().classes('p-4 gap-1'):
                    ui.link(result['title'], result['url']).classes('text-lg font-semibold text-purple-800 hover:text-purple-600')
                    ui.label(result['url']).classes('text-sm text-purple-400')
                    ui.label(result['preview']).classes('text-gray-600 mt-2')
            
        ui.run_javascript('window.scrollTo({top: document.querySelector(".results-section").offsetTop - 20, behavior: "smooth"})')
        

    with ui.column().classes('w-full items-center pt-16 px-4 search-container'):
        with ui.row().classes('items-baseline mb-8'):
            ui.icon('search', size='lg', color='purple').classes('mr-2 self-center')
            ui.label('SearchTogether').classes('text-5xl font-bold bg-gradient-to-r from-purple-800 to-purple-500 bg-clip-text text-transparent leading-tight')

        with ui.column().classes('w-full max-w-2xl mb-12'):
            with ui.row().classes('w-full items-center bg-purple search-bar overflow-hidden'):
                search_input = ui.input(placeholder='Search together...').classes(
                'w-full border-0 focus:ring-0 focus:border-transparent outline-none text-white'
            ).props('borderless input-class=text-white')

            with ui.row().classes('w-full justify-center gap-4 mt-4'):
                with ui.button(icon='tune', color='purple').classes('search-button').on('click', options_panel.toggle):
                    ui.tooltip('Search options')
                with ui.button('Search', color='purple').classes('search-button px-6').on('click', show_results):
                    ui.tooltip('Search')
    
ui.run(reload=False, port=native.find_open_port())