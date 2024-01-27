import os
import re
import ast
import math
import json
import random

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.cluster import KMeans

from .base_selector import BaseSelector

"""'
    代码分数 = 代码结构复杂度 * 代码逻辑复杂度

    （1）定义代码结构复杂度 = sigmoid(sum (归一化的节点数量,  归一化的节点深度,  归一化的节点类型)).
    NodeCount ：表示抽象语法树中的节点数量。
    Depth:  表示抽象语法树的深度，即从根节点到最深层节点的路径长度。
    Types :表示抽象语法树中节点的变量类型数量。

    （2）定义代码逻辑复杂度 = sigmoid(难度 D * 条件复杂度V).
    其中难度是参考软件工程里面哈尔斯特度量 （Halstead Complexity Metrics），条件复杂度是参考软工里面McCabe Cyclomatic complexity，圈复杂度，这个是来衡量程序的复杂性；

    难度 (D)计算公式为：D = (n1 / 2) * (N2 / n2)，表示理解程序所需的精力:
    其中：
    n1：源代码中不同操作符的数量。
    N2：源代码中操作数的总数量。
    n2：源代码中不同操作数的数量。
    在这个公式中，(n1 / 2) 项表示操作符的平均复杂度，N2 / n2 项表示操作数的平均复杂度。难度 D 是这两个复杂度的乘积。

    圈复杂度(V)的计算公式为:  V = E - N + 2
    E: 表示控制流图中边的数量
    N: 表示控制流图中节点的数量

    注意，程序的可能错误和高的圈复杂度有着很大关系，圈复杂度最高的模块和方法，其缺陷个数也可能最多。
    圈复杂度大说明程序代码的判断逻辑复杂，可能质量低，且难于测试和维护
"""


def batch_normalization(x, epsilon=1e-8):
    mean = np.mean(x, axis=0)
    variance = np.var(x, axis=0)
    normalized_x = (x - mean) / np.sqrt(variance + epsilon)
    return normalized_x


def count_nodes(tree):
    # 使用ast模块的NodeVisitor类来遍历抽象语法树并计算节点数量
    class NodeCounter(ast.NodeVisitor):
        def __init__(self):
            self.count = 0

        def generic_visit(self, node):
            self.count += 1
            ast.NodeVisitor.generic_visit(self, node)

    counter = NodeCounter()
    counter.visit(tree)
    return counter.count


def calculate_depth(tree):
    # 使用ast模块的NodeVisitor类来遍历抽象语法树并计算深度
    class DepthCounter(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.max_depth = 0

        def generic_visit(self, node):
            self.depth += 1
            self.max_depth = max(self.max_depth, self.depth)
            ast.NodeVisitor.generic_visit(self, node)
            self.depth -= 1

    counter = DepthCounter()
    counter.visit(tree)
    return counter.max_depth


def count_node_types(tree):
    # 使用ast模块的NodeVisitor类来遍历抽象语法树并计算节点类型数量
    class TypeCounter(ast.NodeVisitor):
        def __init__(self):
            self.types = set()

        def generic_visit(self, node):
            self.types.add(type(node).__name__)
            ast.NodeVisitor.generic_visit(self, node)

    counter = TypeCounter()
    counter.visit(tree)
    return len(counter.types)


def calculate_structure_complexity(code):
    # 解析抽象语法树
    tree = ast.parse(code)

    # 统计节点数量
    node_count = count_nodes(tree)

    # 统计节点深度
    depth = calculate_depth(tree)

    # 统计节点类型数量
    type_count = count_node_types(tree)

    return (node_count, depth, type_count)


def calculate_cyclomatic_complexity(code):
    # 解析抽象语法树
    tree = ast.parse(code)

    # 使用ast模块的NodeVisitor类来遍历抽象语法树并计算圈复杂度
    class CyclomaticComplexityVisitor(ast.NodeVisitor):
        def __init__(self):
            self.complexity = 1  # 默认复杂度为1，表示至少存在一条路径

        def visit_If(self, node):
            self.complexity += 1  # 每个if语句增加1个复杂度
            self.generic_visit(node)

        def visit_For(self, node):
            self.complexity += 1  # 每个for循环增加1个复杂度
            self.generic_visit(node)

        def visit_While(self, node):
            self.complexity += 1  # 每个while循环增加1个复杂度
            self.generic_visit(node)

        def visit_Break(self, node):
            self.complexity += 1  # 每个break语句增加1个复杂度
            self.generic_visit(node)

        def visit_Continue(self, node):
            self.complexity += 1  # 每个continue语句增加1个复杂度
            self.generic_visit(node)

        def visit_Try(self, node):
            self.complexity += 1  # 每个try语句增加1个复杂度
            self.generic_visit(node)

        def visit_ExceptHandler(self, node):
            self.complexity += 1  # 每个异常处理增加1个复杂度
            self.generic_visit(node)

    visitor = CyclomaticComplexityVisitor()
    visitor.visit(tree)
    return visitor.complexity


def count_operators_and_operands(code):
    # 使用正则表达式匹配代码中的操作符和操作数
    operators = re.findall(r"[-+*/%=<>!]+", code)
    operands = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", code)  # 假设操作数由合法的标识符组成

    # 统计操作符和操作数的数量和不重复的数量 ++++ -- /
    operator_count = len(operators)  # 7
    operand_count = len(operands)  # 10
    unique_operator_count = len(set(operators))  # 3
    unique_operand_count = len(set(operands))  # 10

    # 3 / 2  * 10/10

    return operator_count, operand_count, unique_operator_count, unique_operand_count


def calculate_logic_complexity(code):
    # 统计操作符和操作数的数量
    (
        operator_count,
        operand_count,
        unique_operator_count,
        unique_operand_count,
    ) = count_operators_and_operands(code)

    # 计算难度 D
    try:
        difficulty = (unique_operator_count / 2) * (
            operand_count / unique_operand_count
        )
    except:
        difficulty = 0

    # 计算条件复杂度 V
    try:
        cyclomatic_complexity = calculate_cyclomatic_complexity(code)
    except:
        print("1")
        cyclomatic_complexity = 0

    # 计算代码逻辑复杂度
    logic_complexity = difficulty * cyclomatic_complexity

    return logic_complexity


class CodeSelector(BaseSelector):
    def __init__(
        self,
        source_file_path: str = "",
        target_dir: str = "",
        target_file_name: str = "",
        min_boundary: float = 0.125,
        max_boundary: float = 0.5,
        manually_partion_data: bool = True,
        automatically_partion_data: bool = True,
        k_means_cluster_number: int = 2,
    ):
        super(CodeSelector, self).__init__(
            source_file_path, target_dir, target_file_name
        )

        self.target_dir = target_dir
        self.min_boundary = min_boundary
        self.max_boundary = max_boundary
        self.manually_partion_data = manually_partion_data
        self.automatically_partion_data = automatically_partion_data
        self.cluster_number = k_means_cluster_number

    def dump_data_to_file(self):
        return

    def check_and_process(self, codes):
        """
        filter blank lines
        """
        new_codes = []
        for item in codes.split("\n"):
            if len(item) != 0:
                new_codes.append(item)
        codes = "\n".join(new_codes)

        run_time = 0

        """
            syntax check
        """
        error = True
        while error and run_time < 100:
            run_time = run_time + 1
            try:
                ast_tree = ast.parse(codes)
                error = False
            except SyntaxError as e:
                error_line = e.lineno
                lines = codes.split("\n")
                lines[error_line - 1] = "# " + lines[error_line - 1]

                codes = "\n".join(lines)
                error = True
            except:
                error = False

        if run_time == 100:
            print("error")

        return codes

    def __process__(self, data):
        if self.data_format != "alpaca":
            raise ValueError("Data format should be alpaca")

        """
            extract code blocks from data
        """
        dataset = []
        for d in tqdm(data):
            python_codes = re.findall(r"```python([\s\S]+?)```", d["output"])
            dataset.append(
                {
                    "instruction": "Use python code to solve the following problem\n",
                    "input": d["input"],
                    "output": "\n".join(python_codes),
                }
            )

        # '''测试'''
        # code = self.check_and_process(dataset[100]['output'])
        # print(code)
        # '''测试'''
        # condition_count, loop_count, operator_count = analyze_code(code)
        # print("Number of conditions: ", condition_count)
        # print("Number of loops: ", loop_count)
        # print("Number of operators: ", operator_count)

        """
            遍历所有代码
        """

        dataset_cleaned = []
        knowledge_structure_score = []
        logical_score_temp = []

        for item in tqdm(dataset):
            instruction = item["instruction"]
            input_ = item["input"]
            code = item["output"]

            """检查并且修正代码基本错误"""
            code = self.check_and_process(code)

            """代码为空，跳过"""
            if code == "":
                continue

            try:
                """将代码字符串解析为抽象语法树"""
                ast_tree = ast.parse(code)

                dataset_cleaned.append(
                    {
                        "instruction": instruction,
                        "input": input_,
                        "output": "```python\n" + code + "\n```",
                    }
                )
            except Exception as e:
                print("----------------------------")
                print(e)
                print(item)

        print("cleaned dataset size: ", len(dataset_cleaned))
        print("\t example: ", random.choice(dataset_cleaned))

        structure_count = []

        for item in tqdm(dataset_cleaned):
            code = item["output"]
            matches = re.findall(r"```python([\s\S]*?)```", code)
            if len(matches) == 0:
                print("error")
            else:
                codes = ("\n".join(matches)).strip()
                structure_count.append(calculate_structure_complexity(codes))

        # 每个特征归一化
        normalized_x = batch_normalization(structure_count)
        # print('----------------------------------')
        # print(normalized_x)
        # 聚合，mean pooling的方式
        total_features = np.mean(normalized_x, axis=1)
        # print('----------------------------------')
        # print(total_features)

        # 使用Sigmoid函数将特征缩放到0-1之间
        structure_scores = 1 / (1 + np.exp(-total_features))
        # print('----------------------------------')
        # print(structure_scores)

        # print(max(structure_scores))
        # print(min(structure_scores))

        logical_count = []

        for item in tqdm(dataset_cleaned):
            code = item["output"]
            matches = re.findall(r"```python([\s\S]*?)```", code)
            if len(matches) == 0:
                print("error")
            else:
                codes = ("\n".join(matches)).strip()
                try:
                    logical_count.append(calculate_logic_complexity(codes))
                except Exception as e:
                    print(e)
                    print(item)
                    break

        logical_features = np.array(logical_count)
        # print(max(logical_features))
        # print(min(logical_features))

        logical_features_norm = batch_normalization(logical_features)
        # print(max(logical_features_norm))
        # print(min(logical_features_norm))

        # print(logical_features_norm)
        # print(logical_features)
        # 使用Sigmoid函数将特征缩放到0-1之间
        logical_scores = 1 / (1 + np.exp(-logical_features_norm))
        # print('---------------------')
        # print(logical_scores)

        # print(max(logical_scores))
        # print(min(logical_scores))

        # print(dataset_cleaned[np.argmin(logical_features)]['output'])
        # print(dataset_cleaned[np.argmax(logical_features)]['output'])

        code_score = np.multiply(structure_scores, logical_scores)
        # print(code_score)

        """
            结构和逻辑分数的比例，因为结构统计因子多，所以设置权重更低一点
        """

        """划分区间"""
        bins = np.linspace(
            math.floor(code_score.min()), math.ceil(code_score.max()), 41
        )
        # print(list(bins))

        digitized = np.digitize(code_score, bins)

        # '''绘制直方图'''
        # plt.hist(code_score, bins=bins,  color='#4274B0')

        # '''设置X轴和Y轴标签'''
        # plt.xlabel('CIRS score')
        # plt.ylabel('numbers')

        # # '''隐藏y轴'''
        # # plt.yticks([])

        # '''显示图形'''
        # # plt.savefig('CIRS score.png', dpi=500)
        # plt.show()

        """
        分数最大和最小的测试例子
        """

        idx = np.argmin(code_score)
        # print(code_score[idx])
        # print()
        # print(dataset_cleaned[idx]['input'])
        # print(dataset_cleaned[idx]['output'])

        # print('--------------------------------')

        idx = np.argmax(code_score)
        # print(structure_scores[idx])
        # print()
        # print(dataset_cleaned[idx]['input'])
        # print(dataset_cleaned[idx]['output'])

        labels_list = []
        boundary = {"low": 0.125, "high": 0.5}
        data_cleaned_low = []
        data_cleaned_medium = []
        data_cleaned_high = []
        for s, item in zip(code_score, dataset_cleaned):
            if s < boundary["low"]:
                data_cleaned_low.append(item)
                labels_list.append(0)
            elif s > boundary["high"]:
                data_cleaned_high.append(item)
                labels_list.append(2)
            else:
                data_cleaned_medium.append(item)
                labels_list.append(1)

        # print(len(data_cleaned_low))
        # print(len(data_cleaned_medium))
        # print(len(data_cleaned_high))
        labels_numpy = np.array(labels_list)
        # print(labels_numpy)
        # plt.scatter(structure_scores, logical_scores, c=labels_numpy, s=1)
        # plt.xlabel('structure scores')
        # plt.ylabel('logical scores')
        # plt.title('Scatter Plot')

        # plt.savefig('distribution.png', dpi=500)
        # plt.show()

        boundary = {"low": self.min_boundary, "high": self.max_boundary}

        """
            low; medium; high
        """
        labels_list = []

        data_cleaned_low = []
        data_cleaned_medium = []
        data_cleaned_high = []
        for s, item in zip(code_score, dataset_cleaned):
            if s < boundary["low"]:
                data_cleaned_low.append(item)
                labels_list.append(0)
            elif s > boundary["high"]:
                data_cleaned_high.append(item)
                labels_list.append(2)
            else:
                data_cleaned_medium.append(item)
                labels_list.append(1)

        if self.manually_partion_data:
            print("\nManually Partion Result:")
            print("\tSubset 1 size (small CIRS score): ", len(data_cleaned_low))
            print("\tSubset 2 size (medium CIRS score): ", len(data_cleaned_medium))
            print("\tSubset 3 size (high CIRS score): ", len(data_cleaned_high))

            os.makedirs(
                os.path.join(self.target_dir, "manually_pration_results"), exist_ok=True
            )

            with open(
                os.path.join(self.target_dir, "manually_pration_results")
                + "/data_cleaned_low.json",
                "w",
            ) as f:
                json.dump(data_cleaned_low, f, indent=4)

            with open(
                os.path.join(self.target_dir, "manually_pration_results")
                + "/data_cleaned_medium.json",
                "w",
            ) as f:
                json.dump(data_cleaned_medium, f, indent=4)

            with open(
                os.path.join(self.target_dir, "manually_pration_results")
                + "/data_cleaned_high.json",
                "w",
            ) as f:
                json.dump(data_cleaned_high, f, indent=4)

            print(
                f'Results saved to {os.path.join(self.target_dir, "manually_pration_results")}\n'
            )

        if self.automatically_partion_data:
            os.makedirs(
                os.path.join(self.target_dir, "automatically_pration_results"),
                exist_ok=True,
            )

            features = np.vstack((structure_scores, logical_scores)).transpose()
            # print(features)
            # print(features.shape)

            kmeans = KMeans(
                n_clusters=self.cluster_number, random_state=0, max_iter=300
            )
            kmeans.fit(features)

            # 输出每个样本的标签
            labels = kmeans.labels_

            # # 根据标签将原始数据分割为三个簇
            # cluster_1 = features[labels == 0]
            # cluster_2 = features[labels == 1]
            # cluster_3 = features[labels == 2]

            # for i in range(cluster_number):
            #     print(f"Cluster {i+1}")
            #     cluster_ = features[labels == i]

            pation_result = {}
            for item, cluster_id in zip(dataset_cleaned, labels.tolist()):
                if cluster_id in pation_result.keys():
                    pation_result[cluster_id].append(item)
                else:
                    pation_result[cluster_id] = [item]

            print("\nAutomatically Partion Result:")
            for cluster_id in pation_result.keys():
                print(f"\tCluster {cluster_id+1}: {len(pation_result[cluster_id])}")
                with open(
                    os.path.join(self.target_dir, "automatically_pration_results")
                    + f"/data_cluster_{cluster_id+1}.jsonl",
                    "w",
                ) as f:
                    json.dump(pation_result[cluster_id], f, indent=4)

            print(
                f'Results saved to {os.path.join(self.target_dir, "automaticallypration_results")}\n'
            )

        return
