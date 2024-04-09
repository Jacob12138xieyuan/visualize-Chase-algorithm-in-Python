from common import count_attributes, get_all_subsets, get_key_string, is_parent_subset


def input_dependencies() -> list[str]:
    dependencies_input = input("Enter functional dependencies separated by ';' (e.g. A->B;B->C;B->A;A->C):")
    dependencies = dependencies_input.split(';')  # 分割多个函数依赖
    result = []
    for dep in dependencies:
        lhs, rhs = dep.split('->')  # 分割左侧和右侧属性
        lhs_attrs = lhs.split(',')  # 左侧属性列表
        rhs_attrs = rhs.split(',')  # 右侧属性列表
        result.append([lhs_attrs, rhs_attrs])
    return result

def gen_min_covers(fds):
    def closure(left_key, dependencies,use_record=True):
        # eg. left_key {A,B,E}
        closure_set = set(left_key)
        left_key_str = get_key_string(left_key)
        if (use_record & (left_key_str in record_closure)): return left_key,record_closure.get(left_key_str)
        # Loop through fds until no changes in closure_set, to ensure that closure_set is complete
        changed = True
        while changed:
            changed = False
            for fd in dependencies:
                # eg. left {A,B,E}, right {F} closure_set {A,B,E}
                left, right = set(fd[0]), set(fd[1])
                # left ⊆ closure_set && right ⊈ closure_set, add right to closure
                if left.issubset(closure_set) and not right.issubset(closure_set):
                    closure_set.update(right)
                    changed = True
        
        if len(closure_set) == max_attrs:
            if len(left_key) == 1: return left_key,closure_set # but if left_key only contains one attribute, it must be candidate key
            for sub_key in left_key:
                # exclude sub_key and re-gather remaining attributes
                subset = [k for k in left_key if k != sub_key]
                sub_attributes,sub_closure_set = closure(subset,dependencies)
                if len(sub_closure_set) == max_attrs: 
                    # Attention!! sub_attributes must be candidate key, surely, subset = sub_attributes
                    left_key,closure_set =  sub_attributes,sub_closure_set
        
        left_key_str = get_key_string(left_key)
        
        if (use_record & (left_key_str not in record_closure)): 
            record_closure[left_key_str] = closure_set
        return left_key,closure_set
    
    minimal_cover = []
    max_attrs = count_attributes(fds)
    record_closure = {}
    # Remove extraneous attributes from the right-hand side of each FD
    for fd in fds:
        # the left-hand side and right-hand side of a functional dependency
        left, right = set(fd[0]), set(fd[1])
        for attr in right.copy():
            # if right contains multi attributes, we should break it down to single
            # eg. A->B,C -break down-> A->B, A->C
            if attr in left: continue #eg. left {A}, attr A, but {A} -> {A} is meaningless
            closure_left,closure_right = closure(left, fds,True)
            if closure_right.issuperset(attr):
                cover = [list(closure_left), list(attr)]
                if cover not in minimal_cover: minimal_cover.append(cover)

    # Remove redundant functional dependencies
    # eg. remove A->C, since A->B, B->C exist
    def check_cover(dfs,subset):
        '''
        Check whether the complete dfs can be deduced from subset
        '''
        # eg. subset [B->A,A->C], dfs [A->B,B->A,A->C,B->C], absent_subset [A->B,B->C]
        absent_subset = [df for df in dfs if df not in subset]
        for validation_df in absent_subset:
            # eg. validate_df {A}->{B}
            left,right = validation_df[0],validation_df[1]
            _,closure_set = closure(set(left),subset,False)
            if not closure_set.issuperset(set(right)):
                # subset cannot deduce the complete dfs,since dependency validation_df cannot be deduced based on subsest
                return False
        return True

    all_subsets = list(get_all_subsets(minimal_cover,[],0,max_attrs))
    all_minimal_cover = []
    for subset in all_subsets:
        if check_cover(minimal_cover,subset): 
            if not any(is_parent_subset(subset, existing_cover) for existing_cover in all_minimal_cover):
                # if existing_cover [A->B,B->A,B->C] is a minimal cover, the subset [A->B,B->A,B->C,A->C] is redundant
                all_minimal_cover.append(subset)
    return all_minimal_cover


# example1: A->B;B->C;B->A;A->C
# example2: A->A,B;B->A,C;A->C;A,B->C
# example3: A->B,C;B->C,D;D->B;A,B,E->F
# B->D;B->C;C->B;C->D;B->E;C->E
if __name__ == "__main__":
    relations = input_dependencies()
    all_minimal_cover = gen_min_covers(relations)
    result = []
    for cover in all_minimal_cover:
        cover_result = []
        for mini_cover in cover:
            lhs = ','.join(mini_cover[0])  # 左侧属性列表转换为字符串
            rhs = ','.join(mini_cover[1])  # 右侧属性列表转换为字符串
            cover_result.append(f"{lhs}->{rhs}")
        result.append(cover_result)# 组合成函数依赖字符串
    print("Congrats!!! minimal cover generation success:\n{}".format(result))  # 使用分号连接多个函数依赖字符串