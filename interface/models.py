from django.db import models
from decimal import Decimal
# Create your models here.
class Patient(models.Model):
    p_id = models.IntegerField(primary_key=True)
    p_name = models.CharField(max_length=10)
    gender = models.CharField(max_length=2)
    birth = models.DateField()

class Dialysis(models.Model):
    d_id = models.AutoField(primary_key=True)
    p_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    age = models.IntegerField()
    times = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    machine_id = models.CharField(max_length=10)
    bed = models.CharField(max_length=10)
    temperature = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.0'), null=True)
    start_temperature = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.0'), null=True)
    before_weight = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    ideal_weight = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    expect_dehydration = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    transfusion = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    food = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    estimate_dehydration = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    set_dehydration = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    after_weight = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    real_dehydration = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    start_SBP = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    start_DBP = models.IntegerField()
    end_SBP = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    end_DBP = models.IntegerField()
    mode = models.CharField(max_length=10)
    machine = models.CharField(max_length=10)
    start_flow_speed = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    start_blood_speed = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    Ca = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    conductivity = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.0'), null=True)
    channel = models.CharField(max_length=100)
    heparin = models.CharField(max_length=100)
    ESA = models.CharField(max_length=100, null=True)
    coagulation = models.CharField(max_length=20)

class Record(models.Model):
    r_id = models.AutoField(primary_key=True)
    d_id = models.ForeignKey(Dialysis, on_delete=models.CASCADE)
    record_time = models.DateTimeField()
    SBP = models.DecimalField(decimal_places=3, max_digits=10)
    DBP = models.IntegerField()
    pulse = models.IntegerField()
    breath = models.DecimalField(decimal_places=3, max_digits=10)
    blood_speed = models.DecimalField(decimal_places=4, max_digits=10)
    flow_speed = models.IntegerField()
    CVP = models.IntegerField()
    DP = models.DecimalField(decimal_places=4, max_digits=10)
    TMP = models.DecimalField(decimal_places=4, max_digits=10)
    dehydrate_speed = models.DecimalField(decimal_places=4, max_digits=10)
    accumulation = models.DecimalField(decimal_places=4, max_digits=10)
    dialyse_temperature = models.DecimalField(decimal_places=3, max_digits=10)
    heparin_volume = models.DecimalField(decimal_places=4, max_digits=10)
    flush = models.DecimalField(decimal_places=3, max_digits=10, null=True)
    channel_confirmed = models.CharField(max_length=5)
    prediction = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)
    is_idh = models.BooleanField(default=False, null=True)

class Feedback(models.Model):
    f_id = models.AutoField(primary_key=True)
    d_id = models.ForeignKey(Dialysis, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    is_sign = models.BooleanField()
    is_drug = models.BooleanField(null=True)
    is_inject = models.BooleanField(null=True)
    is_setting = models.BooleanField(null=True)
    is_other = models.BooleanField(null=True)

# 1205新增
class Predict(models.Model):
    # 透析、預測時間、當下預測值
    pred_id = models.AutoField(primary_key=True)
    d_id = models.ForeignKey(Dialysis, on_delete=models.CASCADE)
    pred_time = models.DateTimeField(auto_now_add=True)
    pred_idh = models.DecimalField(decimal_places=3, max_digits=10, default=Decimal('0.0'), null=True)

class Warnings(models.Model):
    # 存發生預測的時間、當下預測值、護理師點掉警示的時間點、收到警示時病人的血壓(SBP, DBP)、操作的護理師員工號
    # 1206 仁賢會推Json request
    w_id = models.AutoField(primary_key=True)
    # pred_id = models.ForeignKey(Predict, on_delete=models.CASCADE)
    dismiss_time = models.DateTimeField(auto_now_add=True)
    empNo = models.IntegerField()
    warning_SBP = models.DecimalField(decimal_places=3, max_digits=10)
    warning_DBP = models.IntegerField()