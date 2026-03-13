frappe.pages['dashboard-project'].on_page_load = function(wrapper) {

	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: '70 RTS',
		single_column: true
	});

	let body = $(wrapper).find('.layout-main-section').empty();

	body.append(`

<style>

.dashboard-container{
	padding:20px;
}

.row{
	margin-bottom:20px;
}

.kpi-card{
	color:#fff;
	padding:20px;
	border-radius:12px;
	display:flex;
	flex-direction:column;
	justify-content:center;
	height:110px;
	box-shadow:0 4px 12px rgba(0,0,0,0.1);
}

.kpi-title{
	font-size:14px;
	opacity:0.9;
}

.kpi-value{
	font-size:28px;
	font-weight:bold;
	text-align:right;
	margin-top:10px;
}

.card-revenue{
	background:linear-gradient(135deg,#4facfe,#00f2fe);
}

.card-cost{
	background:linear-gradient(135deg,#ff9a9e,#fad0c4);
}

.card-profit{
	background:linear-gradient(135deg,#43e97b,#38f9d7);
}

.card-percent{
	background:linear-gradient(135deg,#fa709a,#fee140);
}

.dashboard-box{
	background:#fff;
	border-radius:10px;
	padding:20px;
	box-shadow:0 2px 8px rgba(0,0,0,0.08);
	margin-bottom:20px;
}

.table th{
	font-weight:600;
}

.text-right{
	text-align:right;
}

</style>

<div class="dashboard-container">

<div class="row">

<div class="col-md-3">
<div class="kpi-card card-revenue">
<div class="kpi-title">Total Revenue</div>
<div class="kpi-value" id="revenue"></div>
</div>
</div>

<div class="col-md-3">
<div class="kpi-card card-cost">
<div class="kpi-title">Total Cost</div>
<div class="kpi-value" id="cost"></div>
</div>
</div>

<div class="col-md-3">
<div class="kpi-card card-profit">
<div class="kpi-title">Total Profit</div>
<div class="kpi-value" id="profit"></div>
</div>
</div>

<div class="col-md-3">
<div class="kpi-card card-percent">
<div class="kpi-title">Profit %</div>
<div class="kpi-value" id="percent"></div>
</div>
</div>

</div>


<div class="dashboard-box">

<h4>Customer Profit Chart</h4>

<div id="chart"></div>

</div>


<div class="dashboard-box">

<h4>Customer Profit Table</h4>

<table class="table table-hover">

<thead>
<tr>
<th>Customer</th>
<th class="text-right">Revenue</th>
<th class="text-right">Cost</th>
<th class="text-right">Profit</th>
</tr>
</thead>

<tbody id="customer_table"></tbody>

</table>

</div>


<div class="row">

<div class="col-md-6">

<div class="dashboard-box">

<h4>Top Profitable Projects</h4>

<table class="table">

<thead>
<tr>
<th>Project</th>
<th class="text-right">Profit</th>
</tr>
</thead>

<tbody id="profit_projects"></tbody>

</table>

</div>

</div>

<div class="col-md-6">

<div class="dashboard-box">

<h4>Top Loss Projects</h4>

<table class="table">

<thead>
<tr>
<th>Project</th>
<th class="text-right">Loss</th>
</tr>
</thead>

<tbody id="loss_projects"></tbody>

</table>

</div>

</div>

</div>

</div>

`);

	init_dashboard();



/* ---------------- SAMPLE DATA ---------------- */

function get_sample_data(){

	return {

	total_revenue:800000,
	total_cost:500000,

	customers:[
	{customer:"ABC Pvt Ltd",revenue:300000,cost:200000},
	{customer:"XYZ Technologies",revenue:250000,cost:150000},
	{customer:"Global Soft",revenue:150000,cost:120000},
	{customer:"TechNova",revenue:100000,cost:30000}
	],

	projects:[
	{project:"ERP Implementation",profit:120000},
	{project:"Website Development",profit:80000},
	{project:"Mobile App",profit:50000},
	{project:"Data Migration",profit:-20000},
	{project:"Support Contract",profit:-35000}
	]

	}

}



/* ---------------- INIT ---------------- */

function init_dashboard(){

	let data = get_sample_data();
	render_dashboard(data);

}



/* ---------------- DASHBOARD ---------------- */

function render_dashboard(data){

	let total_profit = data.total_revenue - data.total_cost;
	let percent = ((total_profit/data.total_revenue)*100).toFixed(1);

	$("#revenue").html(frappe.format(data.total_revenue,{fieldtype:"Currency"}));
	$("#cost").html(frappe.format(data.total_cost,{fieldtype:"Currency"}));
	$("#profit").html(frappe.format(total_profit,{fieldtype:"Currency"}));
	$("#percent").html(percent+"%");

	render_customer_table(data.customers);
	render_chart(data.customers);
	render_projects(data.projects);

}



/* ---------------- CUSTOMER TABLE ---------------- */

function render_customer_table(customers){

	let rows="";

	customers.forEach(c=>{

	let profit=c.revenue-c.cost;

	rows+=`
	<tr>
	<td>${c.customer}</td>
	<td class="text-right">${frappe.format(c.revenue,{fieldtype:"Currency"})}</td>
	<td class="text-right">${frappe.format(c.cost,{fieldtype:"Currency"})}</td>
	<td class="text-right ${profit>=0?'text-success':'text-danger'}">
	${frappe.format(profit,{fieldtype:"Currency"})}
	</td>
	</tr>
	`;

	});

	$("#customer_table").html(rows);

}



/* ---------------- CHART ---------------- */

function render_chart(customers){

	$("#chart").empty();

	let labels=[];
	let values=[];

	customers.forEach(c=>{
	labels.push(c.customer);
	values.push(c.revenue-c.cost);
	});

	new frappe.Chart("#chart",{

	data:{
	labels:labels,
	datasets:[
	{
	name:"Profit",
	values:values
	}
	]
	},

	type:"bar",
	height:300

	});

}



/* ---------------- PROJECT TABLES ---------------- */

function render_projects(projects){

	let profit_rows="";
	let loss_rows="";

	projects.sort((a,b)=>b.profit-a.profit);

	projects.forEach(p=>{

	if(p.profit>=0){

	profit_rows+=`
	<tr>
	<td>${p.project}</td>
	<td class="text-right text-success">
	${frappe.format(p.profit,{fieldtype:"Currency"})}
	</td>
	</tr>
	`;

	}else{

	loss_rows+=`
	<tr>
	<td>${p.project}</td>
	<td class="text-right text-danger">
	${frappe.format(p.profit,{fieldtype:"Currency"})}
	</td>
	</tr>
	`;

	}

	});

	$("#profit_projects").html(profit_rows);
	$("#loss_projects").html(loss_rows);

}

};