import pandas as pd
import matplotlib.pyplot as plt
import pm4py
import build_petri_net 
import numpy as np

class AnalysisData:
    def __init__(self, data: pd.DataFrame, case_id: str, activity: str, timestamp: str, record_at: str, time_unit: str):
        self.original_data = data
        self.case_id = case_id
        self.activity = activity
        self.timestamp = timestamp
        self.record_at = record_at
        self.time_unit = time_unit
        
        self.original_data[timestamp] = pd.to_datetime(self.original_data[timestamp])
        
        self.original_df_variants = self.original_data.groupby(self.case_id)[self.activity].apply(lambda x: " -> ".join(x)).reset_index()
        self.original_df_variants.columns = [self.case_id, "variants"]
        self.trace_columns = pm4py.stats.get_trace_attributes(self.original_data)
        if self.case_id not in self.trace_columns:
            self.trace_columns.append(self.case_id)
        trace_data = self.original_data[self.trace_columns].drop_duplicates(subset=self.case_id)
        self.original_df_variants = self.original_df_variants.merge(trace_data, on=self.case_id, how='left')
        
        if self.record_at == "end":
            shift_num = 1
            time_column = "start_time"
        elif self.record_at == "start":
            shift_num = -1
            time_column = "end_time"  
            
        self.original_data[time_column] = self.original_data.sort_values(by=[self.case_id, self.timestamp]).groupby(self.case_id)[self.timestamp].shift(shift_num)
        self.original_data[time_column] = self.original_data[time_column].fillna(self.original_data[self.timestamp])
        self.original_data[time_column] = pd.to_datetime(self.original_data[time_column])
        
        seconds = {"Năm": 3600*24*365, "Tháng": 3600*24*30, "Ngày": 3600*24, "Giờ": 3600, "Phút": 60, "Giây": 1}
        
        self.original_data["cycle_time"] = (self.original_data[self.timestamp] - self.original_data[time_column]).dt.total_seconds().abs() / seconds[self.time_unit]
        throughput_df= self.original_data.groupby(self.case_id)["cycle_time"].sum().reset_index(name="throughput_time")
        self.original_df_variants = self.original_df_variants.merge(throughput_df, on=self.case_id)
        self.original_df_variants["variant_freq"] = self.original_df_variants.groupby("variants")[self.case_id].transform('count')
        
        self.update_data()
        
    def update_data(self, min_freq: int = 0):
        """Cập nhật dữ liệu mới"""
        if min_freq == 0:
            self.data = self.original_data.copy()
            self.df_variants = self.original_df_variants.copy()
        else:
            self.df_variants = self.original_df_variants[self.original_df_variants["variant_freq"] >= min_freq].copy()
            self.data = self.original_data[self.original_data[self.case_id].isin(self.df_variants[self.case_id].unique())].copy()
            
        self.df_variants["variant_freq"] = self.df_variants.groupby("variants")[self.case_id].transform('count')
        
        self.freq_model = self.df_variants["variant_freq"].describe().get("25%")
        self.freq_model = int(self.freq_model)
        self.get_model(self.freq_model)
        
        self.case_count = self.data[self.case_id].nunique()
        self.activity_count = self.data[self.activity].nunique()
        self.variant_count = self.df_variants['variants'].nunique()
        self.mean_throughput_time = self.df_variants["throughput_time"].mean()
        self.median_throughput_time = self.df_variants["throughput_time"].median()
        
    def throughput_time_distribution(self):
        fig = plt.figure()  # <-- tạo Figure
        plt.hist(self.df_variants["throughput_time"], bins=20)
        plt.axvline(self.mean_throughput_time, color='red', linestyle='--', label='Trung bình')
        plt.axvline(self.median_throughput_time, color='green', linestyle='--', label='Trung vị')    
        plt.xlabel(f"Throughput Time ({self.time_unit})")
        plt.ylabel("Tần suất")
        plt.legend()
        return fig
        
    def cycle_time_by(self, column: str, top: int = 10, biggest_or_smallest: str = "biggest"):
        grouped = self.data.groupby(column)["cycle_time"].mean()
        sorted_vals = grouped.sort_values(ascending=False if biggest_or_smallest == "smallest" else True).tail(top)
        width, height = compute_barh_figsize(sorted_vals)
        fig = plt.figure(figsize=(width, height))
        sorted_vals.plot(kind='barh')

        plt.title(f"Top {min(top, len(grouped))} {column} có trung bình Cycle Time {'lớn nhất' if biggest_or_smallest == 'biggest' else 'nhỏ nhất'}")
        plt.ylabel(column)
        plt.xlabel(f"Cycle Time ({self.time_unit})")
        
        sorted_vals = sorted_vals.reset_index(name="Cycle Time").sort_values(by='Cycle Time', ascending=False)
        sorted_vals['Cycle Time'] = sorted_vals['Cycle Time'].round(2)
        return fig, sorted_vals
    
    def throughput_time_by(self, column: str, top: int = 10, biggest_or_smallest: str = "biggest"):
        grouped = self.df_variants.groupby(column)["throughput_time"].mean()
        sorted_vals = grouped.sort_values(ascending=False if biggest_or_smallest == "smallest" else True).tail(top)
        width, height = compute_barh_figsize(sorted_vals)
        fig = plt.figure(figsize=(width, height))
        sorted_vals.plot(kind='barh')

        plt.title(f"Top {min(top, len(grouped))} {column} có trung bình Throughput Time {'lớn nhất' if biggest_or_smallest == 'biggest' else 'nhỏ nhất'}")
        plt.ylabel(column)
        plt.xlabel(f"Throughput Time ({self.time_unit})")
        
        sorted_vals = sorted_vals.reset_index(name="Throughput Time").sort_values(by='Throughput Time', ascending=False)
        sorted_vals['Throughput Time'] = sorted_vals['Throughput Time'].round(2)
        return fig, sorted_vals
    
    def frequency_by(self, column: str, top: int = 10, biggest_or_smallest: str = "biggest"):
        activity_counts = self.data[column].value_counts().sort_values(ascending=False if biggest_or_smallest == "smallest" else True).tail(top)
        width, height = compute_barh_figsize(activity_counts)
        fig = plt.figure(figsize=(width, height))
        activity_counts.plot(kind='barh')
        plt.title(f"Top {min(top, len(activity_counts))} {column} có tần suất {'lớn nhất' if biggest_or_smallest == 'biggest' else 'nhỏ nhất'}")
        plt.xlabel("Tần suất")
        plt.ylabel(column)
        return fig, activity_counts.reset_index(name='Tần suất').sort_values(by='Tần suất', ascending=False)

    def variant_frequency(self):
        """Trả về bảng tần suất biến thể"""
        variant_counts = self.df_variants['variants'].value_counts()
        return variant_counts.reset_index(name='Tần suất').rename(columns={'variants': 'Biến thể'}).sort_values(by='Tần suất', ascending=False)

    def get_model(self, freq: int):
        """Lấy Petri net từ dữ liệu theo tần suất"""
        net_cases = self.df_variants[self.df_variants["variant_freq"] >= freq][self.case_id].unique()
        self.net_cases = self.data[self.data[self.case_id].isin(net_cases)]
        self.net, self.im, self.fm = pm4py.discovery.discover_petri_net_inductive(self.net_cases, case_id_key=self.case_id, activity_key=self.activity, timestamp_key=self.timestamp)
        self.bpmn_model = pm4py.convert_to_bpmn(self.net, self.im, self.fm)
        
    def work_count_df(self):
        rework_df = pd.crosstab(self.net_cases[self.case_id], self.net_cases[self.activity])
        work_count_df = rework_df.apply(pd.Series.value_counts).fillna(0).astype(int)
        work_count_df = work_count_df.T.reset_index()
        work_count_df.columns = [f"{col} lần" if col != self.activity else col for col in work_count_df.columns]
        return work_count_df
             
        
class ImprovingData:
    def __init__(self, data: AnalysisData):
        self.analysis_data = data
        self.data = self.analysis_data.original_data
        self.case_id = self.analysis_data.case_id
        self.activity = self.analysis_data.activity
        self.timestamp = self.analysis_data.timestamp
        
        self.data[self.timestamp] = pd.to_datetime(self.data[self.timestamp])
        self.log = pm4py.convert_to_event_log(self.data, case_id_key=self.case_id, activity_key=self.activity, timestamp_key=self.timestamp)
        
        #self.df_arc_time = self.get_arc_time_from_log()
        
        self.current_model = build_petri_net.PetriNetBuilder()
        self.improved_model = build_petri_net.PetriNetBuilder()
        
        self.current_metrics = None
        self.improved_metrics = None
        
    def get_df_from_variants(self, variants):
        list_variants = [" -> ".join(variant) for variant in variants] 
        cases = self.analysis_data.df_variants[self.analysis_data.df_variants['variants'].isin(list_variants)][self.case_id].unique()
        df_with_variants = self.data[self.data[self.case_id].isin(cases)]
        return df_with_variants
    
    def get_arc_time_from_log(self, df_arc_time):
        df_arc_time['prev_activity'] = df_arc_time.groupby(self.case_id)[self.activity].shift(1)
        df_arc_time['prev_activity'].fillna('Start', inplace=True)
        df_arc_time['cycle_time'] = df_arc_time.groupby(self.case_id)[self.timestamp].diff().dt.total_seconds()/(3600*24)
        df_arc_time['cycle_time'] = df_arc_time['cycle_time'].fillna(0)
        df_arc_time.rename(columns={self.activity: 'activity'}, inplace=True)
        df_arc_time = df_arc_time[['prev_activity', 'activity', 'cycle_time']]
        df_arc_time = df_arc_time.groupby(['prev_activity', 'activity']).agg({'cycle_time': 'mean'}).reset_index()

        return df_arc_time
    
    def count_move_on_log_flow(self, alignments):
        move_on_log_counts = {}

        for alignment_dict in alignments:
            log = []
            alignment = alignment_dict.get("alignment", [])
            for move in alignment:
                if move[0] != ">>":
                    log.append(move[0])
            for move in alignment:
                if move[1] == ">>":
                    idx_move = log.index(move[0])
                    prev_move = log[idx_move - 1] if idx_move > 0 else 'Start'
                    next_move = log[idx_move + 1] if idx_move < len(log) - 1 else 'End'
                    flow = f"{prev_move} -> {move[0]} -> {next_move}"
                    move_on_log_counts[flow] = move_on_log_counts.get(flow, 0) + 1
        move_on_log_counts = pd.DataFrame(list(move_on_log_counts.items()), columns=['Luồng hoạt động', 'Tần suất'])
        return move_on_log_counts.sort_values(by='Tần suất', ascending=False)
    
    def get_net_variants(self, net, im, fm):
        variants = []
        simu_log = pm4py.algo.simulation.playout.petri_net.algorithm.apply(net, im, fm)

        from pm4py.statistics.traces.generic.log import case_statistics

        # Lọc trace duy nhất
        unique_traces = case_statistics.get_variant_statistics(simu_log)
        for trace in unique_traces:
            variants.append(trace['variant'])
        return variants
    
    def get_arc_time_from_variants(self, variants):
        arc_time = []
        variant_throughput_time = {}
        df_arc_time = self.get_arc_time_from_log(self.get_df_from_variants(variants))

        for variant in variants:
            throughput_time = []
            for i, activity in enumerate(variant):
                if i > 0:
                    prev_activity = variant[i-1]
                    cycle_time_series = df_arc_time[(df_arc_time['activity'] == activity) & (df_arc_time['prev_activity'] == prev_activity)]['cycle_time']
                    if not cycle_time_series.empty:
                        cycle_time = cycle_time_series.iloc[0]  # Extract the scalar value
                    elif hasattr(self, 'temp_model_cycle_time') and activity in self.temp_model_cycle_time:
                        cycle_time = self.temp_model_cycle_time[activity]
                    else:
                        cycle_time = np.mean(throughput_time)
                    throughput_time.append(cycle_time)
                    new_row = {'prev_activity': prev_activity, 'activity': activity, 'cycle_time': round(cycle_time, 2)}
                    arc_time.append(new_row)
            variant_throughput_time[variant] = sum(throughput_time)
        arc_time = pd.DataFrame(arc_time)
        arc_time = arc_time.drop_duplicates(subset=['prev_activity', 'activity']).sort_values(by='cycle_time', ascending=False)
        arc_time = arc_time.rename(columns={'prev_activity': 'Hoạt động trước', 'activity': 'Hoạt động', 'cycle_time': f'Cycle Time ({self.analysis_data.time_unit})'})
        return arc_time, variant_throughput_time
    
    def get_improvement_metrics(self, net, im, fm):
        """Tính toán các chỉ số cải tiến dựa trên mô hình Petri net và log"""
        
        variants = set()
        fit_trace_count = 0
        fitness_fail_sum = 0
        fail_trace_count = 0
        case_num = len(self.log)

        alignment_trace = pm4py.conformance.conformance_diagnostics_alignments(self.log, net, im, fm)
        move_log_counts = self.count_move_on_log_flow(alignment_trace)
        for alignment_dict in alignment_trace:
            if alignment_dict['fitness'] == 1:
                variants.add(tuple(alignment_dict['alignment']))
                fit_trace_count += 1
            else:
                fitness_fail_sum += alignment_dict['fitness']
                fail_trace_count += 1
        net_variants = self.get_net_variants(net, im, fm)
        arc_time, variant_throughput = self.get_arc_time_from_variants(net_variants)

        metrics = {'Độ phù hợp tổng thế': round(fit_trace_count/case_num, 2),
                'Độ phù hợp của các log lỗi': round(fitness_fail_sum/fail_trace_count, 2) if fail_trace_count > 0 else 1,
                'Số lượng biến thể của mô hình': len(net_variants),
                'Số lượng biến thể khớp với mô hình': len(variants),
                'Trung bình Throughput Time': round(np.mean(list(variant_throughput.values())), 2)
                }
        metrics = pd.DataFrame(list(metrics.items()), columns=['Chỉ số', 'Giá trị'])

        return metrics, move_log_counts, arc_time
    
    def get_petri_net_and_metrics(self, model_type: str, file_path=None, net=None, im=None, fm=None):
        if model_type == "current":
            if file_path:
                self.current_model.load_from_pnml(file_path)
                net, im, fm = self.current_model.get_petri_net()
            else:
                self.current_model.from_existing_net(net, im, fm)
            self.current_metrics, self.current_move_log_counts, self.current_arc_time = self.get_improvement_metrics(net, im, fm)
            self.current_bpmn_model = pm4py.convert_to_bpmn(net, im, fm)
        elif model_type == "improve":
            if file_path:
                self.improved_model.load_from_pnml(file_path)
                net, im, fm = self.improved_model.get_petri_net()
            else:
                self.improved_model.from_existing_net(net, im, fm)
            self.improved_metrics, self.improved_move_log_counts, self.improved_arc_time = self.get_improvement_metrics(net, im, fm)
            self.improved_bpmn_model = pm4py.convert_to_bpmn(net, im, fm)
            
    def export_petri_net(self, model_type: str, file_path: str):
        """Xuất mô hình Petri net ra file PNML"""
        if model_type == "current":
            self.current_model.save_to_pnml(file_path)
        elif model_type == "improve":
            self.improved_model.save_to_pnml(file_path)
            
    def get_temp_model(self, model_type: str, model_state: str):
        self.temp_model = build_petri_net.PetriNetBuilder()
        self.temp_model_cycle_time = self.analysis_data.original_data.groupby(self.activity)['cycle_time'].mean().to_dict()
        
        if model_state == "edit":
            if model_type == "current":
                net, im, fm = self.current_model.get_petri_net()
                self.temp_model_arc_time = self.current_arc_time  
            elif model_type == "improve": 
                net, im, fm = self.improved_model.get_petri_net()
                self.temp_model_arc_time = self.improved_arc_time
                
            self.temp_model.from_existing_net(net=net, initial_marking=im, final_marking=fm)
            
            # for act in self.temp_model.net.transitions:
            #     act_name = act.label
            #     if act_name in self.df_arc_time['activity'].unique():
            #         cycle_time = self.df_arc_time[self.df_arc_time['activity'] == act_name]['cycle_time'].mean()
            #         self.temp_model_cycle_time[act_name] = cycle_time
                    
    
    # def average_throughput_time_by_columns(self):
    #     results = []
    #     df_variants = self.analysis_data.df_variants

    #     for column in self.analysis_data.trace_columns:
    #         if column == self.case_id:
    #             continue
    #         if column not in df_variants.columns:
    #             continue

    #         avg_tp = df_variants.groupby(column)["throughput_time"].mean().reset_index()
    #         avg_tp.columns = ["Value", "Avg Throughput Time"]
    #         avg_tp["Column"] = column
    #         results.append(avg_tp[["Column", "Value", "Avg Throughput Time"]])

    #     return pd.concat(results, ignore_index=True)
   
            
def compute_barh_figsize(data, row_height=0.5, max_width=10):
    """Tính toán kích thước cho biểu đồ barh"""
    num_bars = len(data)
    fig_height = max(4, num_bars * row_height)
    return max_width, fig_height         
        
def draw_model(type: str, rankdir: str = 'TB', net = None, im = None, fm = None, bpmn_model = None):
    """Vẽ mô hình dựa trên loại"""
    if type == "Petri Net":
        return build_petri_net.render_to_tk_image(model_type="Petri Net", net=net, initial_marking=im, final_marking=fm, rankdir=rankdir)
    elif type == "BPMN":
        return build_petri_net.render_to_tk_image(model_type="BPMN", net = bpmn_model, rankdir=rankdir)
    
        